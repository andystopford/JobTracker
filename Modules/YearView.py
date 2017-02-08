from PyQt4 import QtCore, QtGui


class YearView(QtGui.QTableView):
    def __init__(self, parent):
        """The year planner interface"""
        super(YearView, self).__init__(parent)
        self.parent = parent
        horiz_header = self.horizontalHeader()
        horiz_header.setResizeMode(QtGui.QHeaderView.Stretch)
        vert_header = self.verticalHeader()
        vert_header.setResizeMode(QtGui.QHeaderView.Stretch)

    def set_selection_model(self, model):
        """
        Set up a QItemSelectionModel - sends the current and previous selection
        - we want the current ([0]) selection
        """
        super(YearView, self).setModel(model)
        self.connect(self.selectionModel(),
                     QtCore.SIGNAL("selectionChanged(QItemSelection, QItemSelection)"),
                     self.get_selection)

    def get_selection(self):
        indices = self.selectedIndexes()
        self.parent.select_date(indices)


