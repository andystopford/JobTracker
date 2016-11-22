from PyQt4 import QtGui, QtCore


class Epoch:
    def __init__(self, date):
        """ A calendar date - name avoids confusion with built-in modules, etc"""
        self.date = date
        self.event_list = []
        self.dateModel = DateModel()

    def add_start_end(self, start, end, hours, miles):
        event = [start, end, hours, miles]
        self.event_list.append(event)

    def append_times(self, parent, colour):
        col = QtGui.QColor()
        col.setNamedColor(colour)
        #row_count = parent.ui.time_table.rowCount()
        #parent.ui.time_table.insertRow(row_count)
        for list in self.event_list:
            for i, item in enumerate(list):
                list[i] = QtGui.QStandardItem(item)
                #list[i] = QtGui.QTableWidgetItem(item)
                #list[i].setBackgroundColor(col)
                #parent.ui.time_table.setItem(row_count, i, list[i])
        self.dateModel.appendRow(list)
        #self.event_list = []

    def get_model(self):
        return self.dateModel

    def colour_cells(self, colour):
        row = self.dateModel.rowCount() - 1
        col = QtGui.QColor()
        col.setNamedColor(colour)
        for i in range(4):
            cell = self.dateModel.item(row, i)
            cell.setBackground(col)

    def clear(self):
        self.dateModel.clear()


class DateModel(QtGui.QStandardItemModel):
    def __init__(self):
        super(DateModel, self).__init__()
        #self.parent = parent
        self.setColumnCount(4)
        labels = ['Start', 'End', 'Hours', 'Miles', 'Item', 'Cost £']
        self.setHorizontalHeaderLabels(labels)

    def supportedDropActions(self):
        return QtCore.Qt.CopyAction | QtCore.Qt.MoveAction