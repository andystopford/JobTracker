import time
from itertools import cycle, islice

from PyQt5 import QtGui, QtCore
from Ticket import Ticket
from Year import *


class Model(QtGui.QStandardItemModel):
    def __init__(self, parent):
        """The model underlying YearView - contains job tickets
                associated with days."""
        super().__init__(parent)
        self.parent = parent
        self.setRowCount(12)
        self.setColumnCount(37)
        self.name_search_list = []
        self.jobs_search_list = []
        self.notes_search_list = []
        self.setup()

    def setup(self):
        """Labels headers and inserts QStandardItems in each cell"""
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug",
                  "Sep", "Oct", "Nov", "Dec"]
        self.setVerticalHeaderLabels(months)
        log_dates = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        log_dates_cycle = cycle(log_dates)
        nth = lambda i, n, d=None: next(islice(i, n, None), d)
        log_date_labels = [nth(log_dates_cycle, 0) for _ in range(37)]
        self.setHorizontalHeaderLabels(log_date_labels)
        # Colour weekends and weeklog_dates differently and
        # insert QStandardItems in each:
        for row in range(12):
            for col in range(37):
                if (col % 7) - 6 == 0 or (col % 7) - 5 == 0:
                    # Weekends
                    log_date = QtGui.QStandardItem()
                    self.setItem(row, col, log_date)
                    self.item(row, col).setBackground(QtGui.QColor('#bbbbbe'))
                else:
                    # weekdays
                    log_date = QtGui.QStandardItem()
                    self.setItem(row, col, log_date)
                    self.item(row, col).setBackground(QtGui.QColor('#d8d8dc'))

    def set_year(self, year, new):
        """Fills in date numbers and colours any cells with associated
        job tickets
        """
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
                                if self.parent.explorer.ui.rem_chkBox.\
                                        isChecked():
                                    colour = QtGui.QColor(176, 180, 255)
                                else:
                                    colour = self.is_weekday(curr_date)
                            elif ticket_list[0].get_cat() == 'Work':
                                if self.parent.explorer.ui.wrk_chkBox.\
                                        isChecked():
                                    colour = QtGui.QColor(253, 160, 127)
                                else:
                                    colour = self.is_weekday(curr_date)
                            else:
                                if self.parent.explorer.ui.othr_chkBox.\
                                        isChecked():
                                    colour = QtGui.QColor(172, 209, 158)
                                else:
                                    colour = self.is_weekday(curr_date)
                            item.setBackground(colour)
        if len(self.name_search_list) > 0:
            for item in self.name_search_list:
                colour = QtGui.QColor(255, 0, 0)
                item.setBackground(colour)
        if len(self.jobs_search_list) > 0:
            for item in self.jobs_search_list:
                colour = QtGui.QColor(0, 255, 0)
                item.setBackground(colour)
        if len(self.notes_search_list) > 0:
            for item in self.notes_search_list:
                colour = QtGui.QColor(0, 0, 255)
                item.setBackground(colour)
        self.mark_today(year_instance)
        # return to JT setup_year()
        return date_list

    def is_weekday(self, col):
        """For restoring background colour if ticket removed/filtered"""
        if (col % 7) - 6 == 0 or (col % 7) - 5 == 0:
            # Weekends
            colour = QtGui.QColor('#d3d3d6')
        else:
            # weekdays
            colour = QtGui.QColor('#dedee2')
        return colour

    def mark_today(self, year_instance):
        """Outline today and select it"""
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
        name = cat  # + ' ' + str(len(ticket_list) + 1)
        date = self.get_date(row, col)
        ticket.set_date(date)
        ticket.set_name(name)
        ticket.set_cat(cat)
        ticket_list.append(ticket)
        tickets.setData(ticket_list)
        return ticket

    def get_date(self, row, col):
        day = self.item(row, col)
        date = day.child(0, 0).data()  # QDate, e.g. (2016, 7, 15)
        date = date.toString()
        return date

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



