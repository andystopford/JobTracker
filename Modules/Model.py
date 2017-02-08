import time
from itertools import cycle, islice

from PyQt4 import QtGui, QtCore
from Ticket import Ticket
from Year import*


class Model(QtGui.QStandardItemModel):
    def __init__(self, parent):
        """The model underlying YearView - contains job tickets
                associated with days."""
        super(Model, self).__init__(parent)

        self.parent = parent
        self.setRowCount(12)
        self.setColumnCount(37)
        self.setup()

    def setup(self):
        """Labels headers and inserts QStandardItems in each cell"""
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
        """Fills in date numbers and colours any cells with associated job tickets"""
        date_list = []
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
                            if ticket_list[0].get_cat() == 'Removal':
                                colour = QtGui.QColor(132, 136, 244)
                            elif ticket_list[0].get_cat() == 'Work':
                                colour = QtGui.QColor(249, 178, 156)
                            else:
                                colour = QtGui.QColor(252, 234, 162)
                            item.setBackground(colour)

        self.mark_today(year_instance)
        # return to JT setup_year()
        return date_list

    def mark_today(self, year_instance):
        """Outline today"""
        date = time.strftime("%d/%m/%Y")
        if int(date[6:10]) == year_instance.year:
            day = int(date[0:2])
            month = int(date[3:5])
            col = year_instance.get_column(month, day)
            row = month - 1
            self.parent.dateDisplay.mark_today(row, col, True)
        else:
            self.parent.dateDisplay.mark_today(0, 0, False)

    def add_ticket(self, row, col, cat):
        """Adds a job ticket to the currently selected day"""
        ticket = Ticket()
        day_item = self.item(row, col)
        tickets = day_item.child(0, 1)
        ticket_list = tickets.data()
        name = cat # + ' ' + str(len(ticket_list) + 1)
        ticket.set_name(name)
        ticket.set_cat(cat)
        ticket_list.append(ticket)
        tickets.setData(ticket_list)
        return ticket

    def delete_ticket(self, row, col, index):
        """From RClick menu in jobTickets QListWidget"""
        item = self.item(row, col)
        tickets = item.child(0, 1)
        ticket_list = tickets.data()
        del ticket_list[index]
        tickets.setData(ticket_list)
        item.setChild(0, 1, tickets)
        # Revert coloured background for empty list
        if len(ticket_list) == 0:
            if (col % 7) - 6 == 0 or (col % 7) - 5 == 0:
                item.setBackground(QtGui.QColor(160, 195, 255))
            else:
                item.setBackground(QtGui.QColor(195, 218, 255))

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



