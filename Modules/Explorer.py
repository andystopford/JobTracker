import sys

from PyQt5 import QtCore, QtGui, QtWidgets

sys.path.append("./UI")
import os.path
from Explorer_UI import Explorer_Ui
from TimeConverter import *
from Year import *
import time
import serial
import serial.tools.list_ports
#from serial import*
import csv


class Explorer(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent, QtCore.Qt.WindowStaysOnTopHint)
        """Controls for filters, totalling expenses, etc."""
        self.ui = Explorer_Ui()
        self.ui.setup_ui(self)
        self.resize(500, 250)
        self.setWindowTitle("JobTracker Explorer")
        self.parent = parent
        # TODO This path is for testing only!
        self.user_path = "/home/andy/Projects/Programming/Python/JobTracker2" \
                         "/JobTrackerUser/"
        # Signals
        #self.ui.tabWidget.currentChanged.connect(self.tab_changed)
        self.ui.name_clear_button.clicked.connect(self.clear_names)
        self.ui.jobs_clear_button.clicked.connect(self.clear_jobs)
        self.ui.notes_clear_button.clicked.connect(self.clear_notes)
        self.ui.name_search_button.clicked.connect(self.search_name)
        self.ui.jobs_search_button.clicked.connect(self.search_jobs)
        self.ui.notes_search_button.clicked.connect(self.search_notes)
        self.ui.filter_clr_butn.clicked.connect(self.clear_all)
        self.ui.rem_chkBox.stateChanged.connect(self.chkBox_changed)
        self.ui.wrk_chkBox.stateChanged.connect(self.chkBox_changed)
        self.ui.othr_chkBox.stateChanged.connect(self.chkBox_changed)
        self.ui.rem_chkBox.setChecked(True)
        self.ui.wrk_chkBox.setChecked(True)
        self.ui.othr_chkBox.setChecked(True)
        self.ui.costs_table.itemClicked.connect(self.handle_clicked)
        self.ui.costs_table.cellClicked.connect(self.select_day)
        header = self.ui.costs_table.horizontalHeader()
        header.sectionClicked.connect(self.check_all)
        self.ui.connect_button.clicked.connect(self.open_serial)
        self.ui.download_button.clicked.connect(self.download_sel)
        self.ui.delete_button.clicked.connect(self.delete_file)

        self.ticket_list = []
        self.ser = serial.Serial()

    def chkBox_changed(self):
        try:
            self.parent.model.set_year(self.parent.year, False)
        except AttributeError:
            # Occurs on startup before a model has been initialised
            return

    def search_name(self):
        self.search('name')

    def search_jobs(self):
        self.search('jobs')
        self.ui.tabWidget.setCurrentIndex(1)

    def search_notes(self):
        self.search('notes')

    def search(self, type):
        """Searches tickets for entered text"""
        self.ticket_list = []
        if type == 'name':
            del self.parent.model.name_search_list[:]
        if type == 'jobs':
            del self.parent.model.jobs_search_list[:]
        if type == 'notes':
            del self.parent.model.notes_search_list[:]
        names_words = []
        jobs_words = []
        notes_words = []
        model = self.parent.model
        name_search = str(self.ui.name_search_box.toPlainText())
        jobs_search = str(self.ui.jobs_search_box.toPlainText())
        notes_search = str(self.ui.notes_search_box.toPlainText())
        for item in name_search.split():
            names_words.append(item)
        jobs_words.append(jobs_search)
        for item in notes_search.split():
            notes_words.append(item)
        for row in range(12):
            for col in range(37):
                day_item = model.item(row, col)  # i.e. a day QItem
                if day_item.child(0, 1):
                    if day_item.child(0, 1).data():
                        tickets = day_item.child(0, 1).data()
                        for ticket in tickets:
                            # Is the cat filter on?
                            cats = self.check_cat_checked()
                            for cat in cats:
                                if ticket.get_cat() == cat:
                                    self.filter_tkt(ticket, names_words,
                                                    jobs_words,
                                                    notes_words, day_item)
        self.parent.model.set_year(self.parent.year, False)
        self.display_job()

    def check_cat_checked(self):
        checked_list = []
        if self.ui.rem_chkBox.isChecked():
            checked_list.append('Removal')
        if self.ui.wrk_chkBox.isChecked():
            checked_list.append('Work')
        if self.ui.othr_chkBox.isChecked():
            checked_list.append('Other')
        return checked_list

    def filter_tkt(self, ticket, names_words, jobs_words, notes_words,
                   day_item):
        # Now filter YearView highlighting
        name = ticket.get_name()
        job = ticket.get_job()
        notes = ticket.get_notes()
        for item in names_words:
            if item.lower() in name.lower():
                self.parent.model.name_search_list.append(day_item)
                self.ticket_list.append(ticket)
        for item in jobs_words:
            if job:
                if item.lower() == job.lower():
                    self.parent.model.jobs_search_list.append(day_item)
                    self.ticket_list.append(ticket)
        for item in notes_words:
            if notes:
                if item.lower() in notes.lower():
                    # print(row, col, name, day_item)
                    self.parent.model.notes_search_list.append(day_item)

    def clear_names(self):
        self.ui.name_search_box.clear()
        del self.parent.model.name_search_list[:]
        self.parent.model.set_year(self.parent.year, False)

    def clear_jobs(self):
        self.ui.jobs_search_box.clear()
        self.ui.costs_table.clear()
        del self.parent.model.jobs_search_list[:]
        self.parent.model.set_year(self.parent.year, False)

    def clear_notes(self):
        self.ui.notes_search_box.clear()
        del self.parent.model.notes_search_list[:]
        self.parent.model.set_year(self.parent.year, False)

    def clear_all(self):
        self.ui.name_search_box.clear()
        self.ui.jobs_search_box.clear()
        self.ui.notes_search_box.clear()
        self.ui.costs_table.clear()
        del self.parent.model.name_search_list[:]
        del self.parent.model.jobs_search_list[:]
        del self.parent.model.notes_search_list[:]
        self.parent.model.set_year(self.parent.year, False)

    def display_job(self):
        """Display job ticket details for the selected Job"""
        costs_table = self.ui.costs_table
        costs_table.clear()
        costs_table.setHorizontalHeaderLabels(['Date', 'Ticket Name', 'Hours',
                                               'Miles', 'Expenses', 'Payments',
                                               'Select'])
        costs_table.setRowCount(len(self.ticket_list) + 1)
        row = 0
        tc = TimeConverter()
        job_hours = 0
        job_miles = 0
        job_costs = 0
        job_payment = 0
        colour = QtGui.QColor(255, 0, 0)
        for ticket in self.ticket_list:
            ticket_hours = 0
            ticket_miles = 0
            ticket_cost = 0.00
            date = ticket.get_date()
            name = ticket.get_name()
            tracks = ticket.get_tracks()
            exp_list = ticket.get_expenses()
            paid = ticket.get_payment()
            paid = paid[1]
            if paid:    # TODO Bug here?
                paid = float(paid)
                job_payment += paid
                paid = '{0:.2f}'.format(paid)
            for track in tracks:
                hours = track.get_hours()
                hours = tc.get_time_mins(hours)
                ticket_hours += hours
                miles = track.get_miles()
                miles = float(miles)
                ticket_miles += miles
            for exp in exp_list:
                if len(exp) == 2:
                    ticket_cost += float(exp[1])
            job_hours += ticket_hours
            job_miles += ticket_miles
            ticket_hours = tc.get_time_hrs_mins(ticket_hours)
            job_costs += ticket_cost
            ticket_cost = '{0:.2f}'.format(ticket_cost)
            date = QtWidgets.QTableWidgetItem(date)
            name = QtWidgets.QTableWidgetItem(name)
            hours = QtWidgets.QTableWidgetItem(str(ticket_hours))
            miles = QtWidgets.QTableWidgetItem(str(ticket_miles))
            ticket_cost = QtWidgets.QTableWidgetItem(str(ticket_cost))
            payment = QtWidgets.QTableWidgetItem(str(paid))
            costs_table.setItem(row, 0, date)
            costs_table.setItem(row, 1, name)
            costs_table.setItem(row, 2, hours)
            costs_table.setItem(row, 3, miles)
            costs_table.setItem(row, 4, ticket_cost)
            costs_table.setItem(row, 5, payment)
            chk_box = self.get_chk_box()
            costs_table.setItem(row, 6, chk_box)
            row += 1
        # now display totals
        job_hours = tc.get_time_hrs_mins(job_hours)
        job_miles = '{0:.2f}'.format(job_miles)
        job_costs = '{0:.2f}'.format(job_costs)
        job_payment = '{0:.2f}'.format(job_payment)
        total_label = QtWidgets.QTableWidgetItem('Total')
        job_hours = QtWidgets.QTableWidgetItem(str(job_hours))
        job_miles = QtWidgets.QTableWidgetItem(str(job_miles))
        job_costs = QtWidgets.QTableWidgetItem(job_costs)
        job_payment = QtWidgets.QTableWidgetItem(job_payment)
        total_label.setForeground(colour)
        job_hours.setForeground(colour)
        job_miles.setForeground(colour)
        job_costs.setForeground(colour)
        job_payment.setForeground(colour)
        row = costs_table.rowCount() - 1
        costs_table.setItem(row, 0, total_label)
        costs_table.setItem(row, 2, job_hours)
        costs_table.setItem(row, 3, job_miles)
        costs_table.setItem(row, 4, job_costs)
        costs_table.setItem(row, 5, job_payment)

    def total_hours(self):
        """Updates totals when tickets checked/unchecked"""
        tc = TimeConverter()
        hours = 0
        miles = 0
        exps = 0
        payments = 0
        costs_table = self.ui.costs_table
        rows = costs_table.rowCount()
        for i in range(0, rows - 1):
            if costs_table.item(i, 6).checkState() == QtCore.Qt.Checked:
                hrs = costs_table.item(i, 2).text()
                hrs = tc.get_time_mins(hrs)
                hours += hrs
                dist = costs_table.item(i, 3).text()
                miles += float(dist)
                ticket_cost = costs_table.item(i, 4).text()
                exps += float(ticket_cost)
                paid = costs_table.item(i, 5).text()
                if len(paid) > 1:
                    payments += float(paid)
        miles = '{0:.2f}'.format(miles)
        exps = '{0:.2f}'.format(exps)
        payments = '{0:.2f}'.format(payments)
        time = tc.get_time_hrs_mins(hours)
        costs_table.item(rows - 1, 2).setText(str(time))
        costs_table.item(rows - 1, 3).setText(str(miles))
        costs_table.item(rows - 1, 4).setText(str(exps))
        costs_table.item(rows - 1, 5).setText(payments)

    def get_chk_box(self):
        """Prepares a check box for insertion in table"""
        chk_box = QtWidgets.QTableWidgetItem()
        chk_box.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        chk_box.setCheckState(QtCore.Qt.Checked)
        return chk_box

    def handle_clicked(self, item):
        """When a check box is checked/unchecked"""
        self.total_hours()

    def check_all(self, col):
        """Toggle check boxes"""
        row_count = self.ui.costs_table.rowCount()
        for row in range(0, row_count - 1):
            chk_box = self.ui.costs_table.item(row, col)
            if chk_box.checkState() == QtCore.Qt.Checked:
                chk_box.setCheckState(QtCore.Qt.Unchecked)
            else:
                chk_box.setCheckState(QtCore.Qt.Checked)
        self.total_hours()

    def select_day(self, row):
        """Selecting day in main UI from the list in costs_table"""
        ticket = self.ticket_list[row]
        date = ticket.get_date()
        date = time.strptime(date, "%a %b %d %Y")
        year = date[0]
        month = date[1]
        day = date[2]
        # Work out the row and column for this date
        year_instance = Year(self, year)
        col = year_instance.get_column(month, day)
        row = month - 1
        # get the year's model and the day's index from it
        model = self.parent.model_dict[year]
        index = model.index(row, col)
        self.parent.ui.yearView.setCurrentIndex(index)
    ###########################################################################
    # Import Tab
    def open_serial(self):
        """Get list of serial ports, check if tracker is connected and
                send handshake message"""
        # If problems with permission denied for USB port, try
        # sudo chmod 777 /dev/ttyUSB*
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            if 'CP2102 USB to UART' in p[1]:
                port = p[0]
            else:
                self.ui.info_display.append('No serial port found')
        self.ser = serial.Serial(port)
        self.ser.baudrate = 9600
        self.ser.timeout = 1
        if self.ser.isOpen:
            self.ser.close()
        self.ser.open()
        self.ser.write(00)  # wake it up
        msg = 'Opening ' + self.ser.name
        self.ui.info_display.append(msg)
        self.hello()

    def hello(self):
        """Handshake to to tell tracker to upload list of files on sd card"""
        handshake = '<' + 'hello' + '>'  # Key word to instruct Arduino
        msg = handshake.encode('ascii')
        self.ser.write(msg)
        self.read_file_list()

    def read_file_list(self):
        """Makes three attempts to download file list"""
        data = self.ser.readline().strip()
        print(data)
        count = 0
        while len(data) == 0:
            if count < 3:
                #self.ui.info_display.append('No data received')
                count += 1
                data = self.ser.readline().strip()
            else:
                self.ui.info_display.append('Giving up')
                break
        while data:
            if len(data) > 0:
                #self.ui.info_display.append('Receiving data')
                text = data.decode('ascii')
                text = text.strip()
                if len(text) > 9:
                    if text[5] == '.':
                        text = '0' + text
                    self.write_file_list(text)
                data = self.ser.readline()

    def write_file_list(self, fname):
        file_item = QtWidgets.QListWidgetItem()
        file_item.setText(fname)
        self.ui.file_lister.addItem(file_item)

    def download_sel(self):
        """Handshake to instruct tracker to upload selected file. Allows for
        names (in the GUI list) which begin with 0"""
        sel_files = self.ui.file_lister.selectedItems()
        for f in sel_files:
            entry = f.text()
            name = entry.split(" ")
            name = name[0]
            if name[0] == '0':
                name = name[1:]
            handshake = '<' + name + '>'  # Key word to instruct Arduino
            msg = handshake.encode('ascii')
            self.ser.write(msg)
            self.read(name)

    def read(self, name):
        """Makes three attempts to read from serial. If data is received, data
        is decoded line by line and appended to data_list. On completion of
        serial transmission the list of fixes is written to disc."""
        if len(name) == 9:
            name = '0' + name
        y = str('20' + name[4:6])
        m = str(name[2:4])
        d = str(name[0:2])
        name = y + m + d + '.log'
        data_list = []
        data = self.ser.readline()
        count = 0      
        while len(data) == 0:
            if count < 3:
                self.ui.info_display.append('Nothing received')
                count += 1
            else:
                self.ui.info_display.append('Giving up')
                break
            data = self.ser.readline()
        while data:
            if len(data) > 0:
                text = data.decode('ascii')
                text = text.strip()
                self.ui.info_display.append(text)
                self.ui.info_display.moveCursor(QtGui.QTextCursor.End)
                QtWidgets.QApplication.processEvents()  # Let it process GUI events
                if len(text) > 0:
                    data_list.append([text])
                if data == b'\r':
                    break
            data = self.ser.readline()
        if len(data_list) > 0:
            d = os.path.dirname(os.getcwd())  # Get path to parent directory
            log_path = d + '/JobTracker2/Logs/'
            writer = csv.writer(open(log_path + name, 'w+'), delimiter="/")
            for row in data_list:
                writer.writerow(row)
            self.ui.info_display.append('Write complete')
        else:
            self.ui.info_display.append('No data to write')

    def delete_file(self):
        sel_files = self.ui.file_lister.selectedItems()
        for f in sel_files:
            row = self.ui.file_lister.row(f)
            entry = f.text()
            name = entry.split(" ")
            name = name[0]
            if name[0] == '0':
                name = name[1:]
            handshake = '<' + 'D' + name + '>'
            msg = handshake.encode('ascii')
            self.ser.write(msg)
            self.ui.file_lister.takeItem(row)
            self.ui.info_display.append(name + ' Deleted')


###############################################################################
class QColorButton(QtWidgets.QPushButton):
    """Custom Qt Widget to show a chosen color.
    Left-clicking the button shows the color-chooser, while
    right-clicking resets the color to None (no-color).
    """
    colorChanged = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._color = None
        self.setMaximumWidth(32)
        self.pressed.connect(self.onColorPicker)

    def setColor(self, color):
        if color != self._color:
            self._color = color
            self.colorChanged.emit()

        if self._color:
            self.setStyleSheet("background-color: %s;" % self._color)
        else:
            self.setStyleSheet("")

    def color(self):
        return self._color

    def onColorPicker(self):
        '''
        Show color-picker dialog to select color.
        Qt will use the native dialog by default.

        '''
        dlg = QtWidgets.QColorDialog(self)
        if self._color:
            dlg.setCurrentColor(QtGui.QColor(self._color))

        if dlg.exec_():
            self.setColor(dlg.currentColor().name())

    def mousePressEvent(self, e):
        if e.button() == QtCore.Qt.RightButton:
            self.setColor(None)

        return super().mousePressEvent(e)
