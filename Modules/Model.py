from PyQt4 import QtGui, QtCore
from itertools import cycle, islice
from Year import*
from Epoch import*


class Model(QtGui.QStandardItemModel):
    def __init__(self, parent):
        super(Model, self).__init__(parent)
        self.parent = parent
        self.setRowCount(12)
        self.setColumnCount(37)
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        self.setVerticalHeaderLabels(months)
        log_dates = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        log_dates_cycle = cycle(log_dates)
        nth = lambda i, n, d=None: next(islice(i, n, None), d)
        log_date_labels = [nth(log_dates_cycle, 0) for _ in range(37)]
        self.setHorizontalHeaderLabels(log_date_labels)
        # Colour weekends and weeklog_dates differently and insert QStandardItems in each:
        for row in range(12):
            for col in range(37):
                if (col % 7) - 6 == 0 or (col % 7) - 5 == 0:
                    log_date = QtGui.QStandardItem()
                    self.setItem(row, col, log_date)
                    self.item(row, col).setBackground(QtGui.QColor(160, 195, 255))
                else:
                    log_date = QtGui.QStandardItem()
                    self.setItem(row, col, log_date)
                    self.item(row, col).setBackground(QtGui.QColor(195, 218, 255))

    def set_year(self, year):
        date_list = []
        # fill in the appropriate dates, e.g. 1st, 2nd, etc
        year_instance = Year(self, year)
        months = year_instance.get_months()
        for month_num in range(12):
            curr_month = month_num
            month = months[month_num]
            for date in range(len(month)):
                curr_date = date
                date = month[date]
                item = self.item(curr_month, curr_date)
                item_text = str(date)
                if date is not '':
                    date_list.append([curr_date, curr_month, item_text])
                    date = int(date)
                    date_to_log = QtCore.QDate(year, curr_month + 1, date)
                    date = QtGui.QStandardItem()
                    item.setChild(0, 1, date)
                    date.setData(date_to_log)
                    epoch_item = QtGui.QStandardItem()  # holder for epoch inst.
                    item.setChild(0, 2, epoch_item)
                    epoch = Epoch(date_to_log)  # the current 24 hour day
                    epoch_item.setData(epoch)
        # return to JT setup_year()
        return date_list

    def tag_day(self, date, tag):
        """Colour codes days in YearView for work/other"""
        day = date.day()
        month = date.month()
        year = date.year()
        year_instance = Year(self, year)
        col = year_instance.get_column(month, day)
        row = month - 1
        item = self.item(row, col)
        if tag == 'work':
            item.setBackground(QtGui.QColor(255, 213, 140))
        else:
            # Other i.e. not working
            item.setBackground(QtGui.QColor(109, 255, 174))




