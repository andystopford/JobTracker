from PyQt4 import QtCore, QtGui

class DayView(QtGui.QTreeView):
    def __init__(self, parent):
        super(DayView, self).__init__(parent)
        """A Tree to show job tickets for the selected day"""
        self.parent = parent
        self.setHeaderHidden(True)
        self.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        self.setEditTriggers(QtGui.QAbstractItemView.DoubleClicked)
        #self.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.connect(self, QtCore.SIGNAL("customContextMenuRequested(QPoint)"), self.right_click)

    def right_click(self):
        menu = QtGui.QMenu(self)
        edit = QtGui.QAction('Edit', self)
        menu.addAction(edit)
        delete = QtGui.QAction('Delete', self)
        menu.addAction(delete)
        menu.popup(QtGui.QCursor.pos())
        edit.triggered.connect(self.edit_entry)
        delete.triggered.connect(self.delete_item)


    def edit_entry(self):
        index = self.selectedIndexes()[0]
        self.parent.dateModel.edit_item(index)

    def delete_item(self):
        indices = self.selectedIndexes()
        index = indices[0]
        row = index.row()
        self.parent.dateModel.removeRow(row)



