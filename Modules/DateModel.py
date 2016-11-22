from PyQt4 import QtGui, QtCore


class DateModel(QtGui.QStandardItemModel):
    def __init__(self, parent):
        super(DateModel, self).__init__(parent)
        self.parent = parent
        self.setColumnCount(4)
        labels = ['Start', 'End', 'Hours', 'Miles', 'Item', 'Cost £']
        self.setHorizontalHeaderLabels(labels)

    def supportedDropActions(self):
        return QtCore.Qt.CopyAction | QtCore.Qt.MoveAction