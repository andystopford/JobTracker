from PyQt4 import QtGui

class Explorer_Ui(object):
    def __init__(self):
        # Widgets
        self.name_search_box = QtGui.QTextEdit()
        self.notes_search_box = QtGui.QTextEdit()
        self.name_clear_button = QtGui.QPushButton('Clear')
        self.notes_clear_button = QtGui.QPushButton('Clear')
        self.name_search_button = QtGui.QPushButton('Search')
        self.notes_search_button = QtGui.QPushButton('Search')
        self.rem_chkBox = QtGui.QCheckBox('Removals')
        self.wrk_chkBox = QtGui.QCheckBox('Work')
        self.othr_chkBox = QtGui.QCheckBox('Other')
        self.filter_clr_butn = QtGui.QPushButton('Clear All')
        self.apply_button = QtGui.QPushButton('Apply')
        self.tabWidget = QtGui.QTabWidget()

    def setup_ui(self, parent_window):
        central_widget = QtGui.QWidget(parent_window)
        parent_window.setCentralWidget(central_widget)
        # Labels
        label_cat_filter = QtGui.QLabel('Filter By Ticket Category:')
        label_name_search_box = QtGui.QLabel('Search By Ticket Name:')
        label_notes_search_box = QtGui.QLabel('Search In Notes:')
        # Main layout
        box = QtGui.QGridLayout()
        central_widget.setLayout(box)
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
        filters_butn_layout.addWidget(label_notes_search_box, 0, 1)
        filters_butn_layout.addWidget(self.notes_search_box, 1, 1)
        filters_butn_layout.addWidget(self.notes_search_button, 2, 1)
        filters_butn_layout.addWidget(self.notes_clear_button, 3, 1)

        filters_layout.addWidget(self.filter_clr_butn)

        self.tabWidget.addTab(filters_widget, 'Filter')