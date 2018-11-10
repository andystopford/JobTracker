from PyQt5 import QtCore, QtWidgets


class YearView(QtWidgets.QTableView):
    def __init__(self, parent):
        """The year planner interface"""
        super().__init__(parent)
        self.parent = parent
        horiz_header = self.horizontalHeader()
        horiz_header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        vert_header = self.verticalHeader()
        vert_header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

    def set_selection_model(self, model):
        """
        Set up a QItemSelectionModel - sends the current and previous selection
        - we want the current ([0]) selection
        """
        super().setModel(model)
        #self.connect(self.selectionModel(),
        #             QtCore.SIGNAL("selectionChanged(QItemSelection, "
        #                           "QItemSelection)"), self.get_selection)
        selection_model = self.selectionModel()
        selection_model.selectionChanged.connect(self.get_selection)

    def get_selection(self):
        indices = self.selectedIndexes()
        self.parent.select_date(indices)

    def keyPressEvent(self, e):
        """Needed because edit triggers are disabled to prevent view entering
        edit mode on a key press (from jobTracker.py)"""
        if e.key() == QtCore.Qt.Key_F2:
            self.parent.explorer.show()
        return


