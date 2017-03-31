import sys
sys.path.append("./Modules")
from PyQt4 import QtCore, QtGui, Qt
from YearView import*
from MapView import*
from TimeLine import*
from TicketNotes import*
from TrackTable import*
from HoursTable import*
from ExpensesTable import*
from JobTickets import*

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class Ui_mainWindow(object):
    def __init__(self):
        self.button_save = QtGui.QPushButton("Save")
        self.button_back = QtGui.QPushButton("<<")
        self.button_forward = QtGui.QPushButton(">>")
        self.button_test = QtGui.QPushButton("Test")
        self.filter_box = QtGui.QComboBox()
        self.label_year = QtGui.QLabel()
        self.coord_display = QtGui.QLabel('test')
        self.date_display = QtGui.QLabel('Date')
        self.time_slider = QtGui.QSlider(Qt.Qt.Horizontal)
        self.menu_track_cols = QtGui.QMenu()
        self.button_track_cols = QtGui.QPushButton("Track Colours")
        self.button_track_cols.setMenu(self.menu_track_cols)
        self.button_rev_cols = QtGui.QPushButton("Reverse")
        self.from_display = QtGui.QTextEdit()
        self.time_display = QtGui.QTextEdit()
        self.to_display = QtGui.QTextEdit()
        # self.jobTickets = QtGui.QListWidget()
        self.button_add_ticket = QtGui.QPushButton("Add Ticket")
        self.menu_tickets = QtGui.QMenu()
        self.button_add_ticket.setMenu(self.menu_tickets)
        self.time_running = QtGui.QTextEdit()
        self.time_total = QtGui.QTextEdit()
        self.button_start_pause = QtGui.QPushButton("Start")
        self.button_apply = QtGui.QPushButton("Apply")

    def setup_ui(self, parent_window):
        central_widget = QtGui.QWidget(parent_window)
        parent_window.setCentralWidget(central_widget)
        # Import widgets
        self.yearView = YearView(parent_window)
        self.mapView = MapView(parent_window)
        self.jobTickets = JobTickets(parent_window)
        self.ticketNotes = TicketNotes(parent_window)
        self.trackTable = TrackTable(parent_window)
        self.hoursTable = HoursTable(parent_window)
        self.expensesTable = ExpensesTable(parent_window)
        # Widget settings
        self.yearView.setMinimumHeight(320)
        self.filter_box.setInsertPolicy(6)
        self.coord_display.setMaximumHeight(20)
        self.date_display.setMaximumHeight(20)
        self.time_slider.setTickPosition(1)
        self.time_slider.setTickInterval(15)
        self.from_display.setMaximumHeight(30)
        self.time_display.setMaximumHeight(30)
        self.to_display.setMaximumHeight(30)
        self.time_running.setMaximumHeight(30)
        self.time_total.setMaximumHeight(30)
        tt_horiz_header = self.trackTable.horizontalHeader()
        tt_horiz_header.setResizeMode(QtGui.QHeaderView.Stretch)
        ht_horiz_header = self.hoursTable.horizontalHeader()
        ht_horiz_header.setResizeMode(QtGui.QHeaderView.Stretch)
        self.hoursTable.setColumnCount(5)
        self.hoursTable.setRowCount(5)
        self.hoursTable.setHorizontalHeaderLabels(['Start', 'End', 'Hours', 'Miles', 'Notes'])
        et_horiz_header = self.expensesTable.horizontalHeader()
        et_horiz_header.setResizeMode(QtGui.QHeaderView.Stretch)
        self.expensesTable.setColumnCount(2)
        self.expensesTable.setHorizontalHeaderLabels(['Item', 'Cost'])

        # Labels
        label_dayView = QtGui.QLabel('Job Tickets')
        label_dayView.setAlignment(QtCore.Qt.AlignCenter)
        label_dayView.setMaximumHeight(10)
        label_from = QtGui.QLabel('From')
        label_from.setAlignment(QtCore.Qt.AlignCenter)
        label_from.setMaximumHeight(10)
        label_time = QtGui.QLabel('Current Time')
        label_time.setAlignment(QtCore.Qt.AlignCenter)
        label_time.setMaximumHeight(10)
        label_to = QtGui.QLabel('To')
        label_to.setAlignment(QtCore.Qt.AlignCenter)
        label_to.setMaximumHeight(10)
        label_job_id = QtGui.QLabel('Job ID')
        label_job_id.setAlignment(QtCore.Qt.AlignCenter)
        label_job_notes = QtGui.QLabel('Notes')
        label_job_notes.setAlignment(QtCore.Qt.AlignCenter)

        # the basic layout:
        box = QtGui.QGridLayout()
        ##################################################
        # YearView group
        # Top button bar
        top_button_widget = QtGui.QWidget()
        top_button_layout = QtGui.QHBoxLayout()
        top_button_widget.setLayout(top_button_layout)
        #top_button_layout.addWidget(self.filter_box)
        top_button_layout.addWidget(self.button_test)
        top_button_layout.addWidget(self.button_back)
        top_button_layout.addWidget(self.label_year)
        top_button_layout.addWidget(self.button_forward)
        top_button_layout.addWidget(self.button_save)
        self.label_year.setAlignment(Qt.Qt.AlignCenter)
        # Year view section
        top_box = QtGui.QWidget()
        top_box_layout = QtGui.QVBoxLayout()
        top_box.setLayout(top_box_layout)
        top_box_layout.addWidget(top_button_widget)
        top_box_layout.addWidget(self.yearView)
        ###################################################
        # Controls
        splitter_controls = QtGui.QSplitter(Qt.Qt.Horizontal)
        # Map control group
        map_ctrl_box = QtGui.QGroupBox()
        map_ctrl_box.setMaximumWidth(275)
        map_ctrl_box_layout = QtGui.QVBoxLayout()
        map_ctrl_box.setLayout(map_ctrl_box_layout)
        map_ctrl_box_layout.addWidget(self.trackTable)
        map_ctrl_layout = QtGui.QGridLayout()
        map_ctrl_box_layout.addLayout(map_ctrl_layout)
        start_fin_layout = QtGui.QGridLayout()
        map_ctrl_box_layout.addLayout(start_fin_layout)

        align = QtCore.Qt.Alignment(0)
        map_ctrl_layout.addWidget(self.button_track_cols, 0, 0, align)
        map_ctrl_layout.addWidget(self.button_rev_cols, 0, 1, align)
        start_fin_layout.setRowMinimumHeight(0, 5)
        start_fin_layout.setRowMinimumHeight(1, 5)
        start_fin_layout.addWidget(label_from, 0, 0, align)
        start_fin_layout.addWidget(label_time, 0, 1, align)
        start_fin_layout.addWidget(label_to, 0, 2, align)
        start_fin_layout.addWidget(self.from_display, 1, 0, align)
        start_fin_layout.addWidget(self.time_display, 1, 1, align)
        start_fin_layout.addWidget(self.to_display, 1, 2, align)

        # Job control group
        job_ctrl_splitter = QtGui.QSplitter()

        ticket_list_container = QtGui.QWidget()
        ticket_list_layout = QtGui.QVBoxLayout()
        ticket_list_container.setLayout(ticket_list_layout)
        ticket_list_container.setMaximumWidth(110)
        ticket_list_layout.addWidget(self.button_add_ticket)
        ticket_list_layout.addWidget(self.jobTickets)

        job_ctrl_splitter.addWidget(ticket_list_container)
        ticket_ctrl_splitter = QtGui.QSplitter(Qt.Qt.Vertical)
        job_ctrl_splitter.addWidget(ticket_ctrl_splitter)
        notes_splitter = QtGui.QSplitter()

        #ticket_ctrl_splitter.addWidget(self.ticketNotes)
        ticket_ctrl_splitter.addWidget(notes_splitter)
        ticket_ctrl_splitter.addWidget(self.hoursTable)
        ticket_ctrl_splitter.addWidget(self.expensesTable)

        notes_splitter.addWidget(self.ticketNotes)
        timer_container = QtGui.QWidget()
        timer_container.setMaximumWidth(150)
        notes_splitter.addWidget(timer_container)
        timer_layout = QtGui.QGridLayout()
        timer_container.setLayout(timer_layout)
        timer_packer1 = QtGui.QWidget()
        timer_packer2 = QtGui.QWidget()
        timer_layout.addWidget(timer_packer1, 0, 0, align)
        timer_layout.addWidget(timer_packer2, 0, 1, align)
        timer_layout.addWidget(self.time_running, 1, 0, align)
        timer_layout.addWidget(self.time_total, 1, 1, align)
        timer_layout.addWidget(self.button_start_pause, 2, 0, align)
        timer_layout.addWidget(self.button_apply, 2, 1, align)

        ###################################################
        # Map group
        map_grp = QtGui.QGroupBox()
        map_layout = QtGui.QVBoxLayout()
        map_grp.setLayout(map_layout)
        map_info = QtGui.QHBoxLayout()
        map_layout.addLayout(map_info)
        map_info.addWidget(self.coord_display)
        map_info.addWidget(self.date_display)
        map_layout.addWidget(self.mapView)
        map_layout.addWidget(self.time_slider)
        ###################################################
        splitter_top = QtGui.QSplitter(Qt.Qt.Vertical)
        splitter_top.addWidget(top_box)
        splitter_bottom = QtGui.QSplitter(Qt.Qt.Horizontal)
        splitter_top.addWidget(splitter_bottom)
        splitter_bottom.addWidget(map_grp)
        splitter_bottom.addWidget(splitter_controls)
        splitter_controls.addWidget(map_ctrl_box)
        splitter_controls.addWidget(job_ctrl_splitter)
        box.addWidget(splitter_top)
        central_widget.setLayout(box)