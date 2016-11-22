from PyQt4 import QtGui


class TableModel(QtGui.QStandardItemModel):
    def __init__(self, parent):
        super(TableModel, self).__init__(parent)
        self.parent = parent
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(['Start', 'End', 'Hours', 'Miles'])


