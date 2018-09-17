from PyQt5 import QtCore, QtGui, QtWidgets


class TrackTable(QtWidgets.QTableView):
    def __init__(self, parent):
        super().__init__(parent)
        """Table to display track segments selected from map"""
        self.parent = parent
        horiz_header = self.horizontalHeader()
        horiz_header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        #self.connect(self, QtCore.SIGNAL("customContextMenuRequested(QPoint)"),
        #            self.right_click)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.track_list = []

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)
        delete = QtWidgets.QAction('Delete', self)
        menu.addAction(delete)
        menu.popup(QtGui.QCursor.pos())
        delete.triggered.connect(self.delete_item)

    def set_selection_model(self, model):
        """Set up a QItemSelectionModel - sends the current and previous
        selection - we want the current ([0]) selection"""
        super().setModel(model)
        #self.connect(self.selectionModel(),
        #             QtCore.SIGNAL("selectionChanged(QItemSelection, "
        #                           "QItemSelection)"),
        #             self.get_selection)
        selection_model = self.selectionModel()
        selection_model.selectionChanged.connect(self.get_selection)

    def set_row_select(self):
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

    def get_selection(self):
        """Get the text for each item in the selected row"""
        indices = self.selectedIndexes()
        for i, item in enumerate(indices):
            index = indices[i]
            x = self.parent.trackModel.itemFromIndex(index)
            self.track_list.append(x)

    def delete_item(self):
        indices = self.selectedIndexes()
        index = indices[0]
        row = index.row()
        self.parent.trackModel.removeRow(row)
        # TODO clear tracks from map




