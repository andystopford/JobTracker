from PyQt4 import QtGui, QtCore
from DateModel import*

class CurrentDay:
    def __init__(self, date):
        """ A calendar date - name avoids confusion with built-in modules, etc"""
        self.date = date
        self.event_list = []
        #self.dateModel = DateModel(self)    # redundant
    """
    def add_start_end(self, start, end, hours, miles):
        event = [start, end, hours, miles]
        self.event_list.append(event)
        #timeSegment = TimeSegment(start, end, hours, miles)
        #return timeSegment

    def append_times(self, parent, colour):
        col = QtGui.QColor()
        col.setNamedColor(colour)
        row_count = parent.ui.time_table.rowCount()
        parent.ui.time_table.insertRow(row_count)
        for list in self.event_list:
            for i, item in enumerate(list):
                list[i] = QtGui.QTableWidgetItem(item)
                list[i].setBackgroundColor(col)
                parent.ui.time_table.setItem(row_count, i, list[i])
        self.event_list = []

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

    """


class TimeSegment:
    def __init__(self, start, end, hrs, miles):
        self.start = start
        self.end = end
        self.hrs = hrs
        self.miles = miles

    def get_start(self):
        return self.start

    def get_end(self):
        return self.end

    def get_hrs(self):
        return self.hrs

    def get_miles(self):
        return self.miles

