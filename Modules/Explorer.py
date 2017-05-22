import sys

from PyQt4 import QtCore, QtGui

sys.path.append("./UI")
from Explorer_UI import Explorer_Ui
from TimeConverter import *
from Timer import *
from Year import *
from Ticket import Track
import time


class Explorer(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent, QtCore.Qt.WindowStaysOnTopHint)
        """Controls for filters, totalling expenses, etc."""
        self.ui = Explorer_Ui()
        self.ui.setup_ui(self)
        # self.resize(500, 250)
        self.setWindowTitle("JobTracker Explorer")
        self.parent = parent
        # TODO This path is for testing only!
        self.user_path = "/home/andy/Projects/Programming/Python/JobTracker2/JobTrackerUser/"
        self.timer = Timer(self)
        # Signals
        self.ui.tabWidget.currentChanged.connect(self.tab_changed)
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
        self.ui.button_start_pause.clicked.connect(self.start_timer)
        self.ui.button_apply.clicked.connect(self.apply_timer)
        self.ui.button_clear.clicked.connect(self.clear_timer)
        self.ui.ticket_list.itemClicked.connect(self.tkt_selected)

        self.ticket_list = []
        self.timer_tkt = None
        self.timer_dirty = False

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
                                    self.filter_tkt(ticket, names_words, jobs_words,
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

    def filter_tkt(self, ticket, names_words, jobs_words, notes_words, day_item):
        # Now filter YearView highlighting
        name = ticket.get_name()
        job = ticket.get_job()
        notes = ticket.get_notes()
        for item in names_words:
            if item.lower() in name.lower():
                self.parent.model.name_search_list.append(day_item)
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
                                               'Miles', 'Expenses', 'Payments', 'Select'])
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
            date = QtGui.QTableWidgetItem(date)
            name = QtGui.QTableWidgetItem(name)
            hours = QtGui.QTableWidgetItem(str(ticket_hours))
            miles = QtGui.QTableWidgetItem(str(ticket_miles))
            ticket_cost = QtGui.QTableWidgetItem(str(ticket_cost))
            payment = QtGui.QTableWidgetItem(str(paid))
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
        job_costs = '{0:.2f}'.format(job_costs)
        job_payment = '{0:.2f}'.format(job_payment)
        total_label = QtGui.QTableWidgetItem('Total')
        job_hours = QtGui.QTableWidgetItem(str(job_hours))
        job_miles = QtGui.QTableWidgetItem(str(job_miles))
        job_costs = QtGui.QTableWidgetItem(job_costs)
        job_payment = QtGui.QTableWidgetItem(job_payment)
        total_label.setTextColor(colour)
        job_hours.setTextColor(colour)
        job_miles.setTextColor(colour)
        job_costs.setTextColor(colour)
        job_payment.setTextColor(colour)
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
        payments = '{0:.2f}'.format(payments)
        time = tc.get_time_hrs_mins(hours)
        costs_table.item(rows - 1, 2).setText(str(time))
        costs_table.item(rows - 1, 3).setText(str(miles))
        costs_table.item(rows - 1, 4).setText(str(exps))
        costs_table.item(rows - 1, 5).setText(payments)

    def get_chk_box(self):
        """Prepares a check box for insertion in table"""
        chk_box = QtGui.QTableWidgetItem()
        chk_box.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        chk_box.setCheckState(QtCore.Qt.Checked)
        return chk_box

    def handle_clicked(self, item):
        # if item.checkState() == QtCore.Qt.Checked:
        #    print('row', item.row())
        #    print('checkstate', item.checkState())
        self.total_hours()

    # Time ###################################################
    def start_timer(self):
        self.timer.timer_start()
        self.ui.button_start_pause.clicked.disconnect(self.start_timer)
        self.ui.button_start_pause.clicked.connect(self.pause_timer)
        self.ui.button_start_pause.setText('Pause')
        self.ui.progress_bar.show()
        self.ui.progress_bar.setRange(0, 0)
        self.timer_dirty = True

    def pause_timer(self):
        curr_time = self.timer.timer_pause()
        self.ui.time_total.setText(curr_time)
        self.ui.button_start_pause.clicked.disconnect(self.pause_timer)
        self.ui.button_start_pause.clicked.connect(self.start_timer)
        self.ui.button_start_pause.setText('Start')
        self.ui.progress_bar.setRange(0, 1)
        self.ui.progress_bar.hide()
        self.ui.button_apply.setEnabled(True)
        self.ui.button_clear.setEnabled(True)

    def tab_changed(self, e):
        if e == 2:
            self.refresh_today()

    def refresh_today(self):
        self.ui.ticket_list.clear()
        self.ui.time_notes.clear()
        self.ui.time_notes.setPlaceholderText("Notes")
        todays_tkts = self.get_today()
        if todays_tkts:
            for tkt in todays_tkts:
                name = tkt.get_name()
                name = QtGui.QListWidgetItem(name)
                self.ui.ticket_list.addItem(name)

    def get_today(self):
        date = time.strftime("%d/%m/%Y")
        year = int(date[6:10])
        year_instance = Year(self, year)
        day = int(date[0:2])
        month = int(date[3:5])
        col = year_instance.get_column(month, day)
        row = month - 1
        model = self.parent.model_dict[year]
        todays_tkts = model.get_ticket_list(row, col)
        return todays_tkts

    def tkt_selected(self, e):
        selection = e.text()
        todays_tkts = self.get_today()
        for tkt in todays_tkts:
            if tkt.get_name() == selection:
                self.timer_tkt = tkt
                #self.ui.button_apply.setEnabled(True)

    def apply_timer(self):
        self.parent.dirty = True
        if self.timer_tkt:
            if self.ui.time_notes.text():
                notes = self.ui.time_notes.text()
            else:
                notes = 'Timer'
            tot_time = self.ui.time_total.toPlainText()
            self.tkt_add_track(self.timer_tkt, tot_time, notes)
            self.clear_timer()

            self.ui.timer_warning.clear()
        else:
            self.timer_warning()

    def timer_warning(self):
        warning = 'Warning: No ticket set/selected for today'
        self.ui.timer_warning.setText(warning)
        self.ui.timer_warning.setStyleSheet('color: red')

    def tkt_add_track(self, ticket, tot_time, notes):
        colour = QtGui.QColor(195, 218, 255)
        brush = QtGui.QBrush(colour)
        track = Track('', '', tot_time, '0', notes, brush)
        ticket.add_track(track)
        if self.parent.selected_indices:
            self.parent.display_tickets()

    def clear_timer(self):
        self.timer.timer_clear()
        self.ui.time_running.setText('')
        self.ui.time_total.clear()
        self.ui.timer_warning.clear()
        self.timer_dirty = False
        self.ui.button_apply.setEnabled(False)
        self.ui.button_clear.setEnabled(False)


###############################################################################
class QColorButton(QtGui.QPushButton):
    """Custom Qt Widget to show a chosen color.
    Left-clicking the button shows the color-chooser, while
    right-clicking resets the color to None (no-color).
    """
    colorChanged = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(QColorButton, self).__init__(*args, **kwargs)

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
        dlg = QtGui.QColorDialog(self)
        if self._color:
            dlg.setCurrentColor(QtGui.QColor(self._color))

        if dlg.exec_():
            self.setColor(dlg.currentColor().name())

    def mousePressEvent(self, e):
        if e.button() == QtCore.Qt.RightButton:
            self.setColor(None)

        return super(QColorButton, self).mousePressEvent(e)
