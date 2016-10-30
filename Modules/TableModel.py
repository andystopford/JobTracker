from PyQt4 import QtGui, QtCore

class TableModel(QtGui.QStandardItemModel):
    def __init__(self, parent):
        super(TableModel, self).__init__(parent)
        self.parent = parent
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(['Start', 'End', 'Hours'])


