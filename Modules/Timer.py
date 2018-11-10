
from PyQt5 import QtCore, QtGui
from Ticket import Track
from TimeConverter import TimeConverter
from Year import Year


class Timer:
    def __init__(self, parent):
        """Timer to record hours working at the computer and record them as a
        track for a selected ticket. Only a ticket from the current day can
        be used."""
        self.parent = parent
        self.qTimer = QtCore.QTimer()
        self.qTimer.timeout.connect(self.display_time)
        self.total_time = 0
        self.start = 0
        self.ticket_list = []
        self.timer_tkt = None
        self.timer_dirty = False

    def fill_menu(self):
        """Fill menu_curr_tickets with the names of any tickets set
        for today"""
        self.parent.ui.menu_curr_tickets.clear()
        todays_tkts = self.get_today()
        for tkt in todays_tkts:
            self.parent.ui.menu_curr_tickets.addAction(tkt.get_name())
        if self.timer_tkt:
            self.parent.ui.button_sel_ticket.setText(self.timer_tkt.get_name())

    def select_ticket(self, name):
        """Get selected ticket from menu_curr_tickets and make it the
        current timed ticket"""
        name = name.text()
        self.parent.ui.button_sel_ticket.setText(name)
        todays_tkts = self.get_today()
        for tkt in todays_tkts:
            if tkt.get_name() == name:
                self.timer_tkt = tkt
                self.parent.ui.button_start_pause.setEnabled(True)

    def get_today(self):
        """Get list of today's tickets from the model"""
        date = QtCore.QDate.currentDate()
        date = date.toString('dd/MM/yyyy')
        year = int(date[6:10])
        year_instance = Year(self, year)
        day = int(date[0:2])
        month = int(date[3:5])
        col = year_instance.get_column(month, day)
        row = month - 1
        model = self.parent.model_dict[year]
        todays_tkts = model.get_ticket_list(row, col)
        return todays_tkts

    def display_time(self):
        """Show time since timer started"""
        now = QtCore.QTime.currentTime()
        elapsed = self.start.secsTo(now)
        disp_time = TimeConverter.get_formatted_hrs_mins_secs(self, elapsed)
        self.parent.ui.time_running.setText(disp_time)

    def start_timing(self):
        """Start timer, reset start button mode to pause, start spinner
        and flag self as dirty"""
        self.start = QtCore.QTime.currentTime()
        self.display_time()
        self.qTimer.start(1000)  # Interval at which timer checks time & 
        # calls display_time()
        self.parent.ui.button_start_pause.clicked.disconnect(self.start_timing)
        self.parent.ui.button_start_pause.clicked.connect(self.pause)
        self.parent.ui.button_start_pause.setText('Pause')
        self.timer_dirty = True
        self.parent.spinner.start()

    def pause(self):
        """Pause timer so that it can either be re-started or the recorded
        time applied"""
        stop = QtCore.QTime.currentTime()
        elapsed = self.start.secsTo(stop)
        self.qTimer.stop()
        self.total_time += elapsed
        # divide by sixty to get minutes - comment out for testing
        minutes = int(self.total_time/60)
        # Comment out next line if not testing
        #minutes = self.total_time
        disp_time = TimeConverter.get_time_hrs_mins(self, minutes)
        self.parent.ui.time_total.setText(disp_time)
        self.parent.ui.button_start_pause.clicked.disconnect(self.pause)
        self.parent.ui.button_start_pause.clicked.connect(self.start_timing)
        self.parent.ui.button_start_pause.setText('Start')
        self.parent.ui.button_apply.setEnabled(True)
        self.parent.ui.button_clear.setEnabled(True)
        self.parent.spinner.stop()

    def apply_timer(self):
        """Apply recorded time to the timed ticket"""
        self.parent.dirty = True
        if self.timer_tkt:
            notes = 'Timer'
            tot_time = self.parent.ui.time_total.text()
            self.tkt_add_track(self.timer_tkt, tot_time, notes)
            self.clear()

    def tkt_add_track(self, ticket, tot_time, notes):
        """Add track to the timed ticket and display it in hoursTable
        if today is currently selected"""
        colour = QtGui.QColor(195, 218, 255)
        brush = QtGui.QBrush(colour)
        track = Track('', '', tot_time, '0', notes, brush)
        ticket.add_track(track)
        if self.parent.selected_indices:
            self.parent.display_tickets()

    def clear(self):
        """Clear timer display and reset controls ready for a new
        timing session"""
        self.parent.ui.time_running.setText('')
        self.parent.ui.time_total.clear()
        self.timer_dirty = False
        self.parent.ui.button_apply.setEnabled(False)
        self.parent.ui.button_clear.setEnabled(False)
        self.parent.ui.time_total.clearFocus()
        self.total_time = 0



