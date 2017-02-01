import time
from itertools import cycle, islice

from PyQt4 import QtGui, QtCore
from Ticket import Ticket
from Year import*


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

    def set_year(self, year, new):
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
                    item.setChild(0, 0, date)
                    date.setData(date_to_log)
                    # other data
                    if new:
                        tickets = QtGui.QStandardItem()
                        ticket_list = []
                        tickets.setData(ticket_list)
                        item.setChild(0, 1, tickets)
                    else:
                        ticket_list = item.child(0, 1).data()
                        if len(ticket_list) > 0:
                            if ticket_list[0].get_type() == 'Removal':
                                colour = QtGui.QColor(94, 89, 255)
                            elif ticket_list[0].get_type() == 'Work':
                                colour = QtGui.QColor(255, 139, 37)
                            else:
                                colour = QtGui.QColor(127, 104, 255)
                            item.setBackground(colour)

        self.mark_today(year_instance)
        # return to JT setup_year()
        return date_list

    def mark_today(self, year_instance):
        date = time.strftime("%d/%m/%Y")
        if int(date[6:10]) == year_instance.year:
            day = int(date[0:2])
            month = int(date[3:5])
            col = year_instance.get_column(month, day)
            row = month - 1
            item = self.item(row, col)
            item.setBackground(QtGui.QColor(109, 255, 174))

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

    def test(self, row, col, tag):
        """proves access to model item from row/col"""
        item = self.item(row, col)
        test_list = ['a', 'b']
        child = QtGui.QStandardItem()
        child.setData(test_list)
        item.setChild(0, 0, child)
        result = item.child(0, 0)
        if tag == 'work':
            item.setBackground(QtGui.QColor(255, 0, 0))
            print(result.data())
        else:
            # Other i.e. not working
            item.setBackground(QtGui.QColor(109, 255, 174))

    def add_ticket(self, row, col, type):
        """Adds a job ticket to the currently selected day"""
        ticket = Ticket()
        day_item = self.item(row, col)
        tickets = day_item.child(0, 1)
        ticket_list = tickets.data()
        name = type # + ' ' + str(len(ticket_list) + 1)
        ticket.set_name(name)
        ticket.set_type(type)
        ticket_list.append(ticket)
        tickets.setData(ticket_list)
        #print(day_item.child(0, 0).data())
        #print(day_item.child(0, 1).data())
        #print(day_item.child(0, 2).data()) #list of Ticket objects
        #for tkt in day_item.child(0, 2).data():
        #    print(tkt.get_name())

    def get_ticket_list(self, row, col):
        day_item = self.item(row, col)
        tickets = day_item.child(0, 1)
        ticket_list = tickets.data()
        return ticket_list

    def get_ticket(self, row, col, name):
        day_item = self.item(row, col)
        tickets = day_item.child(0, 1)
        ticket_list = tickets.data()
        for tkt in ticket_list:
            if tkt.get_name() == name:
                return tkt





