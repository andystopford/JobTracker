from ExpensesTable import *
from HoursTable import *
from PyQt4 import QtGui


class Explorer_Ui(object):
    def __init__(self):
        # Widgets
        # Search
        self.jobs_search_box = QtGui.QTextEdit()
        self.name_search_box = QtGui.QTextEdit()
        self.notes_search_box = QtGui.QTextEdit()
        self.jobs_clear_button = QtGui.QPushButton('Clear')
        self.name_clear_button = QtGui.QPushButton('Clear')
        self.notes_clear_button = QtGui.QPushButton('Clear')
        self.jobs_search_button = QtGui.QPushButton('Search')
        self.name_search_button = QtGui.QPushButton('Search')
        self.notes_search_button = QtGui.QPushButton('Search')
        self.rem_chkBox = QtGui.QCheckBox('Removals')
        self.wrk_chkBox = QtGui.QCheckBox('Work')
        self.othr_chkBox = QtGui.QCheckBox('Other')
        self.filter_clr_butn = QtGui.QPushButton('Clear All')
        self.apply_button = QtGui.QPushButton('Apply')
        # Jobs
        self.costs_table = QtGui.QTableWidget()
        ht_horiz_header = self.costs_table.horizontalHeader()
        ht_horiz_header.setResizeMode(QtGui.QHeaderView.Stretch)
        self.costs_table.setColumnCount(7)
        self.costs_table.setRowCount(5)
        # self.costs_table.setMaximumWidth(550)
        self.costs_table.setHorizontalHeaderLabels(['Date', 'Ticket Name',
                                                    'Hours',
                                                    'Miles', 'Expenses',
                                                    'Payments', 'Select'])
        # Import
        self.connect_button = QtGui.QPushButton('Open Serial')
        self.download_button = QtGui.QPushButton('Download File')
        self.delete_button = QtGui.QPushButton('Delete File')
        self.file_lister = QtGui.QListWidget()
        self.info_display = QtGui.QTextEdit()

        self.tabWidget = QtGui.QTabWidget()

    def setup_ui(self, parent_window):
        self.central_widget = QtGui.QWidget(parent_window)
        parent_window.setCentralWidget(self.central_widget)
        # Labels
        label_cat_filter = QtGui.QLabel('Filter By Ticket Category:')
        label_name_search_box = QtGui.QLabel('Search By Ticket Name:')
        label_job_search_box = QtGui.QLabel('Search By Job Name:')
        label_notes_search_box = QtGui.QLabel('Search In Notes:')
        # Main layout
        box = QtGui.QGridLayout()
        self.central_widget.setLayout(box)
        box.addWidget(self.tabWidget)
        # Filters tab
        filters_widget = QtGui.QWidget()
        filters_layout = QtGui.QVBoxLayout()
        filters_widget.setLayout(filters_layout)
        chk_box_layout = QtGui.QHBoxLayout()
        chk_box_layout.addWidget(self.rem_chkBox)
        chk_box_layout.addWidget(self.wrk_chkBox)
        chk_box_layout.addWidget(self.othr_chkBox)
        filters_layout.addWidget(label_cat_filter)
        filters_layout.addLayout(chk_box_layout)
        filters_butn_layout = QtGui.QGridLayout()

        filters_layout.addLayout(filters_butn_layout)

        filters_butn_layout.addWidget(label_name_search_box, 0, 0)
        filters_butn_layout.addWidget(self.name_search_box, 1, 0)
        filters_butn_layout.addWidget(self.name_search_button, 2, 0)
        filters_butn_layout.addWidget(self.name_clear_button, 3, 0)

        filters_butn_layout.addWidget(label_job_search_box, 0, 1)
        filters_butn_layout.addWidget(self.jobs_search_box, 1, 1)
        filters_butn_layout.addWidget(self.jobs_search_button, 2, 1)
        filters_butn_layout.addWidget(self.jobs_clear_button, 3, 1)

        filters_butn_layout.addWidget(label_notes_search_box, 0, 2)
        filters_butn_layout.addWidget(self.notes_search_box, 1, 2)
        filters_butn_layout.addWidget(self.notes_search_button, 2, 2)
        filters_butn_layout.addWidget(self.notes_clear_button, 3, 2)

        filters_layout.addWidget(self.filter_clr_butn)
        
        # Jobs tab
        job_widget = QtGui.QWidget()
        job_layout = QtGui.QHBoxLayout()
        details_layout = QtGui.QVBoxLayout()
        job_widget.setLayout(job_layout)
        job_layout.addLayout(details_layout)
        details_layout.addWidget(self.costs_table)

        # Import tab
        import_widget = QtGui.QWidget()
        import_layout = QtGui.QGridLayout()
        import_widget.setLayout(import_layout)
        import_layout.addWidget(self.connect_button, 0, 0)
        import_layout.addWidget(self.file_lister, 1, 0)
        import_layout.addWidget(self.download_button, 2, 0)
        import_layout.addWidget(self.delete_button, 3, 0)
        import_layout.addWidget(self.info_display, 0, 1, 4, 1)


        self.tabWidget.addTab(filters_widget, 'Filter')
        self.tabWidget.addTab(job_widget, 'Jobs')
        self.tabWidget.addTab(import_widget, 'Import GPS File')