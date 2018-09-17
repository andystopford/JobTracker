import sys
sys.path.append("./Modules")
from PyQt5 import QtCore, Qt, QtWidgets
from YearView import*
from MapView import*
from TimeLine import*
from TicketNotes import*
from TrackTable import*
from HoursTable import*
from ExpensesTable import*
from PaymentTable import*
from JobTickets import*
import DarkStyle
from RangeSlider import QHRangeSlider

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtWidgets.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig)


class Ui_mainWindow:
    def __init__(self):
        self.button_save = QtWidgets.QPushButton("Save")
        self.button_back = QtWidgets.QPushButton("<<")
        self.button_forward = QtWidgets.QPushButton(">>")
        self.button_explore = QtWidgets.QPushButton("Explorer")
        self.filter_box = QtWidgets.QComboBox()
        self.label_year = QtWidgets.QLabel()
        self.coord_display = QtWidgets.QLabel('test')
        self.date_display = QtWidgets.QLabel('Date')
        self.time_slider = QtWidgets.QSlider(Qt.Qt.Horizontal)
        self.menu_track_cols = QtWidgets.QMenu()
        self.button_map = QtWidgets.QRadioButton("Map")
        self.button_terrain = QtWidgets.QRadioButton("Terrain")
        self.button_sat = QtWidgets.QRadioButton("Satellite")
        self.button_clear = QtWidgets.QPushButton("Clear Route")
        #self.button_to = QtWidgets.QPushButton("Pick To")
        self.button_rhide = QtWidgets.QPushButton("Hide Routing")
        self.button_route = QtWidgets.QPushButton("Route")
        self.from_box = QtWidgets.QLineEdit()
        self.to_box = QtWidgets.QLineEdit()

        self.button_track_cols = QtWidgets.QPushButton("Track Colours")
        self.button_track_cols.setMenu(self.menu_track_cols)
        self.button_rev_cols = QtWidgets.QPushButton("Reverse")

        self.range_slider = QHRangeSlider()

        self.from_display = QtWidgets.QTextEdit()
        self.time_display = QtWidgets.QTextEdit()
        self.to_display = QtWidgets.QTextEdit()
        # self.jobTickets = QtWidgets.QListWidget()
        self.button_add_ticket = QtWidgets.QPushButton("Add Ticket")
        self.menu_tickets = QtWidgets.QMenu()
        self.button_add_ticket.setMenu(self.menu_tickets)
        self.job_name_box = QtWidgets.QLineEdit()
        # Timer
        self.button_sel_ticket = QtWidgets.QPushButton("Ticket")
        self.menu_curr_tickets = QtWidgets.QMenu()
        self.button_sel_ticket.setMenu(self.menu_curr_tickets)
        self.button_start_pause = QtWidgets.QPushButton("Start")
        self.button_apply = QtWidgets.QPushButton("Apply")
        self.button_clear = QtWidgets.QPushButton("Clear")
        self.button_apply.setEnabled(False)
        self.button_clear.setEnabled(False)
        self.spinner_widget = QtWidgets.QWidget()
        self.time_running = QtWidgets.QLineEdit()
        self.time_total = QtWidgets.QLineEdit()

    def setup_ui(self, parent_window):
        central_widget = QtWidgets.QWidget(parent_window)
        parent_window.setCentralWidget(central_widget)
        # Import widgets
        self.yearView = YearView(parent_window)
        self.mapView = MapView(parent_window)
        self.jobTickets = JobTickets(parent_window)
        self.ticketNotes = TicketNotes(parent_window)
        self.trackTable = TrackTable(parent_window)
        self.hoursTable = HoursTable(parent_window)
        self.expensesTable = ExpensesTable(parent_window)
        self.paymentTable = PaymentTable(parent_window)
        # Widget settings
        self.button_map.setChecked(True)
        self.job_name_box.setPlaceholderText('Job Name')
        self.yearView.setMinimumHeight(320)
        self.filter_box.setInsertPolicy(6)
        self.coord_display.setMaximumHeight(20)
        self.date_display.setMaximumHeight(20)
        self.time_slider.setTickPosition(1)
        self.time_slider.setTickInterval(15)
        self.from_display.setMaximumHeight(30)
        self.time_display.setMaximumHeight(30)
        self.to_display.setMaximumHeight(30)
        tt_horiz_header = self.trackTable.horizontalHeader()
        tt_horiz_header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        ht_horiz_header = self.hoursTable.horizontalHeader()
        ht_horiz_header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        et_horiz_header = self.expensesTable.horizontalHeader()
        et_horiz_header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        pt_horiz_header = self.paymentTable.horizontalHeader()
        pt_horiz_header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        ht_vert_header = self.hoursTable.verticalHeader()
        ht_vert_header.hide()
        pt_vert_header = self.paymentTable.verticalHeader()
        pt_vert_header.hide()
        self.hoursTable.setColumnCount(5)
        self.hoursTable.setRowCount(5)
        #self.hoursTable.setMinimumWidth(550)
        self.hoursTable.setHorizontalHeaderLabels(['Start', 'End', 'Hours',
                                                   'Miles', 'Notes'])
        self.expensesTable.setColumnCount(2)
        self.expensesTable.setHorizontalHeaderLabels(['Item', 'Cost'])
        self.paymentTable.setColumnCount(2)
        self.paymentTable.setRowCount(1)
        self.paymentTable.setMaximumHeight(60)
        # Have to load stylesheet for these. Gawdnosewhy.
        ht_horiz_header.setStyleSheet(DarkStyle.load_stylesheet_pyqt5())
        et_horiz_header.setStyleSheet(DarkStyle.load_stylesheet_pyqt5())
        pt_horiz_header.setStyleSheet(DarkStyle.load_stylesheet_pyqt5())
        self.menu_tickets.setStyleSheet(DarkStyle.load_stylesheet_pyqt5())
        self.menu_curr_tickets.setStyleSheet(DarkStyle.load_stylesheet_pyqt5())
        self.menu_track_cols.setStyleSheet(DarkStyle.load_stylesheet_pyqt5())

        # Labels
        label_dayView = QtWidgets.QLabel('Job Tickets')
        label_dayView.setAlignment(QtCore.Qt.AlignCenter)
        label_dayView.setMaximumHeight(10)
        label_from = QtWidgets.QLabel('From')
        label_from.setAlignment(QtCore.Qt.AlignCenter)
        label_from.setMaximumHeight(12)
        label_time = QtWidgets.QLabel('Current Time')
        label_time.setAlignment(QtCore.Qt.AlignCenter)
        label_time.setMaximumHeight(12)
        label_to = QtWidgets.QLabel('To')
        label_to.setAlignment(QtCore.Qt.AlignCenter)
        label_to.setMaximumHeight(12)
        label_job_id = QtWidgets.QLabel('Job ID')
        label_job_id.setAlignment(QtCore.Qt.AlignCenter)
        label_job_notes = QtWidgets.QLabel('Notes')
        label_job_notes.setAlignment(QtCore.Qt.AlignCenter)

        # the basic layout:
        box = QtWidgets.QGridLayout()
        ##################################################
        # YearView group
        # Top button bar
        top_button_widget = QtWidgets.QWidget()
        top_button_layout = QtWidgets.QHBoxLayout()
        top_button_widget.setLayout(top_button_layout)
        top_button_layout.addWidget(self.button_explore)
        top_button_layout.addWidget(self.button_back)
        top_button_layout.addWidget(self.label_year)
        top_button_layout.addWidget(self.button_forward)
        top_button_layout.addWidget(self.button_save)
        self.label_year.setAlignment(Qt.Qt.AlignCenter)
        # Year view section
        top_box = QtWidgets.QWidget()
        top_box_layout = QtWidgets.QVBoxLayout()
        top_box.setLayout(top_box_layout)
        top_box_layout.addWidget(top_button_widget)
        top_box_layout.addWidget(self.yearView)
        ###################################################
        # Controls
        splitter_controls = QtWidgets.QSplitter(Qt.Qt.Horizontal)
        # Map control group
        map_ctrl_box = QtWidgets.QGroupBox()
        map_ctrl_box.setMaximumWidth(275)
        map_ctrl_box_layout = QtWidgets.QVBoxLayout()
        map_ctrl_box.setLayout(map_ctrl_box_layout)
        map_ctrl_box_layout.addWidget(self.button_map)
        map_ctrl_box_layout.addWidget(self.button_terrain)
        map_ctrl_box_layout.addWidget(self.button_sat)

        routing_group = QtWidgets.QGroupBox('Routing')
        routing_layout = QtWidgets.QVBoxLayout()
        routing_group.setLayout(routing_layout)
        route_input_layout = QtWidgets.QHBoxLayout()
        route_ctrls_layout = QtWidgets.QHBoxLayout()

        routing_layout.addLayout(route_input_layout)
        routing_layout.addLayout(route_ctrls_layout)
        map_ctrl_box_layout.addWidget(routing_group)

        route_input_layout.addWidget(self.from_box)
        route_input_layout.addWidget(self.to_box)
        route_ctrls_layout.addWidget(self.button_route)
        route_ctrls_layout.addWidget(self.button_rhide)
        route_ctrls_layout.addWidget(self.button_clear)

        track_table_group = QtWidgets.QGroupBox('Tracks')
        track_table_layout = QtWidgets.QVBoxLayout()
        track_table_group.setLayout(track_table_layout)
        track_table_layout.addWidget(self.trackTable)

        map_ctrl_box_layout.addWidget(track_table_group)
        track_ctrl_layout = QtWidgets.QGridLayout()
        track_table_layout.addLayout(track_ctrl_layout)

        slider_group = QtWidgets.QGroupBox('Tracker Range')
        slider_group.setMaximumHeight(80)
        slider_layout = QtWidgets.QGridLayout()
        slider_group.setLayout(slider_layout)
        slider_layout.addWidget(self.range_slider, 0, 0)

        self.range_slider.setFixedHeight(30)
        map_ctrl_box_layout.addWidget(slider_group)

        start_fin_group = QtWidgets.QGroupBox('Timeline')
        start_fin_group.setMaximumHeight(80)
        start_fin_layout = QtWidgets.QGridLayout()
        start_fin_group.setLayout(start_fin_layout)
        map_ctrl_box_layout.addWidget(start_fin_group)

        align = QtCore.Qt.Alignment(0)
        track_ctrl_layout.addWidget(self.button_track_cols, 0, 0, align)
        track_ctrl_layout.addWidget(self.button_rev_cols, 0, 1, align)
        start_fin_layout.addWidget(label_from, 0, 0, align)
        start_fin_layout.addWidget(label_time, 0, 1, align)
        start_fin_layout.addWidget(label_to, 0, 2, align)
        start_fin_layout.addWidget(self.from_display, 1, 0, align)
        start_fin_layout.addWidget(self.time_display, 1, 1, align)
        start_fin_layout.addWidget(self.to_display, 1, 2, align)

        # Job control group
        # job_ctrl_splitter = QtWidgets.QSplitter()
        ticket_ctrl_container = QtWidgets.QWidget()
        ticket_ctrl_layout = QtWidgets.QVBoxLayout()
        ticket_ctrl_container.setLayout(ticket_ctrl_layout)

        ticket_container = QtWidgets.QGroupBox()
        ticket_timer_layout = QtWidgets.QHBoxLayout()
        ticket_list_layout = QtWidgets.QGridLayout()
        ticket_container.setLayout(ticket_timer_layout)
        ticket_list_container = QtWidgets.QWidget()
        ticket_timer_layout.addWidget(ticket_list_container)
        timer_container = QtWidgets.QGroupBox('Timer')
        ticket_timer_layout.addWidget(timer_container)
        ticket_list_container.setLayout(ticket_list_layout)

        spinner_layout = QtWidgets.QGridLayout()
        timer_container.setLayout(spinner_layout)

        spinner_layout.addWidget(self.button_sel_ticket, 0, 0)
        spinner_layout.addWidget(self.spinner_widget, 1, 0, 2, 1)
        spinner_layout.addWidget(self.time_running, 3, 0)
        spinner_layout.addWidget(self.button_start_pause, 0, 1)
        spinner_layout.addWidget(self.button_apply, 1, 1)
        spinner_layout.addWidget(self.button_clear, 2, 1)
        spinner_layout.addWidget(self.time_total, 3, 1)

        self.button_add_ticket.setMaximumWidth(100)
        self.jobTickets.setMaximumWidth(100)
        ticket_list_layout.addWidget(self.button_add_ticket, 0, 0)
        ticket_list_layout.addWidget(self.jobTickets, 1, 0)

        ticket_list_layout.addWidget(self.job_name_box, 0, 1)
        ticket_list_layout.addWidget(self.ticketNotes, 1, 1)

        ticket_ctrl_layout.addWidget(ticket_container)
        ticket_ctrl_layout.addWidget(self.hoursTable)
        ticket_ctrl_layout.addWidget(self.expensesTable)
        ticket_ctrl_layout.addWidget(self.paymentTable)
        ###################################################
        # Map group
        map_grp = QtWidgets.QGroupBox()
        map_layout = QtWidgets.QVBoxLayout()
        map_grp.setLayout(map_layout)
        map_info = QtWidgets.QHBoxLayout()
        map_layout.addLayout(map_info)
        map_info.addWidget(self.coord_display)
        map_info.addWidget(self.date_display)
        map_layout.addWidget(self.mapView)
        map_layout.addWidget(self.time_slider)
        ###################################################
        splitter_top = QtWidgets.QSplitter(Qt.Qt.Vertical)
        splitter_top.addWidget(top_box)
        splitter_bottom = QtWidgets.QSplitter(Qt.Qt.Horizontal)
        splitter_top.addWidget(splitter_bottom)
        splitter_bottom.addWidget(map_grp)
        splitter_bottom.addWidget(splitter_controls)
        splitter_bottom.setSizes([800, 800])
        splitter_controls.addWidget(map_ctrl_box)
        splitter_controls.addWidget(ticket_ctrl_container)
        box.addWidget(splitter_top)
        central_widget.setLayout(box)