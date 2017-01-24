import bisect
from PyQt4 import QtGui, QtCore, Qt

KEY, NODE = range(2)


class BranchNode(object):
    def __init__(self, name, parent=None):
        super(BranchNode, self).__init__()
        self.name = name
        self.parent = parent
        self.children = []

    def __lt__(self, other):
        if isinstance(other, BranchNode):
            return self.order_key() < other.order_key()
        return False

    def order_key(self):
        return self.name.lower()

    def to_string(self):
        return self.name

    def __len__(self):
        return len(self.children)

    def child_at_row(self, row):
        assert 0 <= row < len(self.children)
        return self.children[row][NODE]

    def row_of_child(self, child):
        for i, item in enumerate(self.children):
            if item[NODE] == child:
                return i
        return -1

    def child_with_key(self, key):
        if not self.children:
            return None
        # Causes a -3 deprecation warning. Solution will be to
        # reimplement bisect_left and provide a key function.
        i = bisect.bisect_left(self.children, (key, None))
        if i < 0 or i >= len(self.children):
            return None
        if self.children[i][KEY] == key:
            return self.children[i][NODE]
        return None

    def insert_child(self, child):
        child.parent = self
        bisect.insort(self.children, (child.order_key(), child))

    def has_leaves(self):
        if not self.children:
            return False
        return isinstance(self.children[0], LeafNode)


class LeafNode(object):
    def __init__(self, fields, parent=None):
        super(LeafNode, self).__init__()
        self.parent = parent
        self.fields = fields

    def order_key(self):
        return "\t".join(self.fields).lower()

    def to_string(self, separator="\t"):
        return separator.join(self.fields)

    def __len__(self):
        return len(self.fields)

    def as_record(self):
        record = []
        branch = self.parent
        while branch is not None:
            record.insert(0, branch.to_string())
            branch = branch.parent
        assert record and not record[0]
        record = record[1:]
        return record + self.fields

    def field(self, column):
        assert 0 <= column <= len(self.fields)
        return self.fields[column]


class TreeOfTableModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super(TreeOfTableModel, self).__init__(parent)
        self.columns = 0
        self.root = BranchNode("")
        self.headers = []

    def load(self, filename, nesting, separator):
        assert nesting > 0
        self.nesting = nesting
        self.root = BranchNode("")
        exception = None
        fh = None
        try:
            for line in codecs.open(str(filename), "rU", "utf8"):
                if not line:
                    continue
                self.add_record(line.split(separator), False)
        except IOError as e:
            exception = e
        finally:
            if fh is not None:
                fh.close()
            self.reset()
            for i in range(self.columns):
                self.headers.append("Column #{0}".format(i))
            if exception is not None:
                raise exception

    def add_record(self, fields, callReset=True):
        assert len(fields) > self.nesting
        root = self.root
        branch = None
        for i in range(self.nesting):
            key = fields[i].lower()
            branch = root.childWithKey(key)
            if branch is not None:
                root = branch
            else:
                branch = BranchNode(fields[i])
                root.insertChild(branch)
                root = branch
        assert branch is not None
        items = fields[self.nesting:]
        self.columns = max(self.columns, len(items))
        branch.insertChild(LeafNode(items, branch))
        if callReset:
            self.reset()

    def as_record(self, index):
        leaf = self.nodeFromIndex(index)
        if leaf is not None and isinstance(leaf, LeafNode):
            return leaf.as_record()
        return []

    def row_count(self, parent):
        node = self.nodeFromIndex(parent)
        if node is None or isinstance(node, LeafNode):
            return 0
        return len(node)

    def column_count(self, parent):
        return self.columns

    def data(self, index, role):
        if role == Qt.TextAlignmentRole:
            return QVariant(int(Qt.AlignTop | Qt.AlignLeft))
        if role != Qt.DisplayRole:
            return QVariant()
        node = self.nodeFromIndex(index)
        assert node is not None
        if isinstance(node, BranchNode):
            return (QVariant(node.toString())
                    if index.column() == 0 else QVariant(QString("")))
        return QVariant(node.field(index.column()))

    def header_data(self, section, orientation, role):
        if (orientation == Qt.Horizontal and
                    role == Qt.DisplayRole):
            assert 0 <= section <= len(self.headers)
            return QVariant(self.headers[section])
        return QVariant()

    def index(self, row, column, parent):
        assert self.root
        branch = self.nodeFromIndex(parent)
        assert branch is not None
        return self.createIndex(row, column,
                                branch.childAtRow(row))

    def parent(self, child):
        node = self.nodeFromIndex(child)
        if node is None:
            return QModelIndex()
        parent = node.parent
        if parent is None:
            return QModelIndex()
        grandparent = parent.parent
        if grandparent is None:
            return QModelIndex()
        row = grandparent.rowOfChild(parent)
        assert row != -1
        return self.createIndex(row, 0, parent)

    def node_from_index(self, index):
        return (index.internalPointer()
                if index.isValid() else self.root)