from PyQt4 import QtGui


class TrackModel(QtGui.QStandardItemModel):
    def __init__(self, parent):
        super(TrackModel, self).__init__(parent)
        """Model to contain track segments selected from map to
        display in trackTable"""
        self.parent = parent
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(['Start', 'End', 'Hours', 'Miles',
                                        'Show'])
        self.itemChanged.connect(self.toggle_row)

    def toggle_row(self, item):
        if item.isCheckable():
            # print('TrackModel: ', item.checkState())
            if item.checkState():
                return
                # print('checked')
            else:
                # print('unchecked')
                self.parent.remove_segment(item.row())

    def reset(self):
        self.setHorizontalHeaderLabels(['Start', 'End', 'Hours', 'Miles',
                                        'Show'])


