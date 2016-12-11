from PyQt4 import QtGui


class TrackModel(QtGui.QStandardItemModel):
    def __init__(self, parent):
        super(TrackModel, self).__init__(parent)
        """Model to contain track segments selected from map to
        display in trackTable"""
        self.parent = parent
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(['Start', 'End', 'Hours', 'Miles'])


