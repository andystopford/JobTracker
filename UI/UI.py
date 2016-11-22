import sys
sys.path.append("./Modules")
from PyQt4 import QtCore, QtGui, Qt
from YearView import*
from MapView import*
from TimeLine import*

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
        self.time_table = QtGui.QTableView()
        #self.time_table = QtGui.QTableWidget()
        self.from_display = QtGui.QTextEdit()
        self.time_display = QtGui.QTextEdit()
        self.to_display = QtGui.QTextEdit()
        # TODO - replace with treeWidget?
        self.job_tickets = QtGui.QTreeView()
        #self.job_time_table = QtGui.QTableWidget()
        self.job_expenses_table = QtGui.QTableWidget()
        self.job_notes = QtGui.QTextEdit()
        self.button_removals = QtGui.QRadioButton('Removals')
        self.button_other_work = QtGui.QRadioButton('Other Work')
        self.button_other = QtGui.QRadioButton('Non Work')

    def setup_ui(self, parent_window):
        central_widget = QtGui.QWidget(parent_window)
        parent_window.setCentralWidget(central_widget)
        # Import widgets
        self.yearView = YearView(parent_window)
        self.mapView = MapView(parent_window)
        self.timeLine = TimeLine(parent_window)
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
        tt_horiz_header = self.time_table.horizontalHeader()
        tt_horiz_header.setResizeMode(QtGui.QHeaderView.Stretch)
        jet_horiz_header = self.job_expenses_table.horizontalHeader()
        jet_horiz_header.setResizeMode(QtGui.QHeaderView.Stretch)
        #self.time_table.setColumnCount(4)
        # jtt_horiz_header = self.job_time_table.horizontalHeader()
        # jtt_horiz_header.setResizeMode(QtGui.QHeaderView.Stretch)
        # et_horiz_header = self.job_expenses_table.horizontalHeader()
        # et_horiz_header.setResizeMode(QtGui.QHeaderView.Stretch)
        # self.job_time_table.setColumnCount(4)
        self.job_expenses_table.setColumnCount(2)
        #labels = ['Start', 'End', 'Hours', 'Miles']
        #self.time_table.setHorizontalHeaderLabels(labels)
        #self.job_tickets.setHorizontalHeaderLabels(labels)
        labels = ['Item', '£']
        self.job_expenses_table.setHorizontalHeaderLabels(labels)

        # Labels
        label_job_tickets = QtGui.QLabel('Job Tickets')
        label_job_tickets.setAlignment(QtCore.Qt.AlignCenter)
        label_job_tickets.setMaximumHeight(10)
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
        top_button_layout.addWidget(self.filter_box)
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
        map_ctrl_box_layout.addWidget(self.time_table)
        start_fin_layout = QtGui.QGridLayout()
        map_ctrl_box_layout.addLayout(start_fin_layout)

        align = QtCore.Qt.Alignment(0)
        start_fin_layout.setRowMinimumHeight(0, 5)
        start_fin_layout.setRowMinimumHeight(1, 5)
        start_fin_layout.addWidget(label_from, 0, 0, align)
        start_fin_layout.addWidget(label_time, 0, 1, align)
        start_fin_layout.addWidget(label_to, 0, 2, align)
        start_fin_layout.addWidget(self.from_display, 1, 0, align)
        start_fin_layout.addWidget(self.time_display, 1, 1, align)
        start_fin_layout.addWidget(self.to_display, 1, 2, align)

        # Job control group
        job_ctrl_box = QtGui.QGroupBox()
        #job_ctrl_box.setMaximumWidth(275)
        job_ctrl_layout = QtGui.QVBoxLayout()
        job_ctrl_box.setLayout(job_ctrl_layout)
        radio_but_container = QtGui.QWidget()
        radio_but_layout = QtGui.QHBoxLayout()
        radio_but_container.setLayout(radio_but_layout)
        radio_but_layout.addWidget(self.button_removals)
        radio_but_layout.addWidget(self.button_other_work)
        radio_but_layout.addWidget(self.button_other)
        job_ctrl_layout.addWidget(radio_but_container)
        job_ctrl_layout.addWidget(label_job_tickets)
        job_ctrl_layout.addWidget(self.job_tickets)
        # job_ctrl_layout.addWidget(self.job_time_table)
        job_ctrl_layout.addWidget(self.job_expenses_table)
        job_ctrl_layout.addWidget(self.job_notes)
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
        splitter_controls.addWidget(job_ctrl_box)
        box.addWidget(splitter_top)
        central_widget.setLayout((box))