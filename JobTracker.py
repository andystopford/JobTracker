#!/usr/bin/python3.4
import sys
sys.path.append("./Modules")
sys.path.append("./UI")
# sys.path.append("./Scripts")
from PyQt4 import QtCore, QtGui, Qt
import datetime
from UI import Ui_mainWindow
from IO import*
from Model import*
from YearView import*
from MapView import*
from GpsAnalyser import*
from TrackPoint import*
from TimeLine import*
from DateDisplay import*
from TimeConverter import*
from TableModel import*


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_mainWindow()
        self.ui.setup_ui(self)
        self.setWindowTitle("JobTracker")

        # Signals
        self.ui.button_test.clicked.connect(self.test)
        self.ui.button_back.clicked.connect(self.year_back)
        self.ui.button_forward.clicked.connect(self.year_forward)
        self.ui.time_slider.valueChanged.connect(self.get_curr_time)
        self.ui.button_add.clicked.connect(self.add_times)
        ##################################################
        # Initialise
        today = datetime.date.today()
        self.model_dict = {}
        self.key_list = []  # temp store for model_dict keys
        self.point_list = []
        self.year = today.year
        self.dirty = False
        dataIO = DataIO(self)   # Put this somewhere else
        dataIO.get_gpx()
        self.dateDisplay = DateDisplay(self.ui.yearView)

        self.tableModel = TableModel(self)
        self.proxy_model = QtGui.QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.tableModel)
        self.ui.time_table.setModel(self.proxy_model)
        self.ui.time_table.setSortingEnabled(True)
        self.time_block = 1  # keeps track of number of work blocks
        self.selected_indices = []
        self.init_model()

    def test(self):
        model = self.model_dict[self.year]
        indices = self.ui.yearView.selectedIndexes()
        row = indices[0].row()
        col = indices[0].column()
        date = model.item(row, col)
        date = date.child(0, 1)
        date = (date.data())
        model.tag_day(date, 'work')

    def add_times(self):
        """Move work times from display boxes to the Model and
        to time_table's model, TableModel() instance."""
        model = self.model_dict[self.year]
        indices = self.selected_indices
        # print(indices[0].row(), indices[0].column())
        row = indices[0].row()
        col = indices[0].column()
        date = model.item(row, col)
        date = date.child(0, 1)
        date = (date.data())
        start = self.ui.start_display.toPlainText()
        end = self.ui.end_display.toPlainText()
        hours = self.ui.hours_display.toPlainText()
        times = model.add_start_stop(date, start, end, hours)
        time_list = []
        for col in range(times.columnCount()):
            time = times.child(1, col).data()
            time_list.append(QtGui.QStandardItem(time))
        self.tableModel.appendRow(time_list)
        self.tableModel.setHorizontalHeaderLabels(['Start', 'End', 'Hours'])
        self.ui.start_display.clear()
        self.ui.end_display.clear()
        self.ui.hours_display.clear()
        self.time_block += 1

    def keyPressEvent(self, e):
        if self.ui.mapView.hasFocus() or self.ui.time_slider.hasFocus():
            if e.key() == QtCore.Qt.Key_Enter:
                time_events = self.ui.timeLine.mark_time()
                # time_events = start_time, end_time, hours_done, self.point_list
                self.display_times(time_events)
            if e.key() == QtCore.Qt.Key_Z:
                self.mapView.zoom_tracker()

    def display_times(self, time_events):
        """Display the start, end and hours for selected part
        of track"""
        self.ui.start_display.setText(time_events[0])
        self.ui.start_display.setAlignment(Qt.Qt.AlignCenter)
        self.ui.end_display.setText(time_events[1])
        self.ui.end_display.setAlignment(Qt.Qt.AlignCenter)
        self.ui.hours_display.setText(time_events[2])
        self.ui.hours_display.setAlignment(Qt.Qt.AlignCenter)
        self.ui.mapView.marker_calc(time_events[0], time_events[3])
        if len(time_events[3]) == 2:
            self.add_times()

    def init_model(self):
        """Model initialised - called at startup so calendar dates
        can be filled in, and added to model_dict"""
        if self.year not in self.model_dict:
            model = Model(self)
            model.set_year(self.year)
            self.model_dict[self.year] = model
        self.model = self.model_dict[self.year]
        self.ui.yearView.setModel(self.model)
        self.ui.yearView.set_selection_model(self.model)
        self.ui.label_year.setText(str(self.year))
        dataIO = DataIO(self)
        log_list = dataIO.get_logs(self.year)
        date_list = self.model.set_year(self.year)
        self.dateDisplay.setup(date_list, log_list)
        self.ui.yearView.setItemDelegate(self.dateDisplay)

    def year_back(self):
        self.year -= 1
        self.init_model()

    def year_forward(self):
        self.year += 1
        self.init_model()

    def get_track(self, date):
        """Gets GPS data for selected day and displays it"""
        date = date.toString(1)
        date = date.replace('-', '')
        gpsAnalyser = GpsAnalyser(self)
        self.point_list = gpsAnalyser.get_data(date)
        self.ui.mapView.draw_track(self.point_list)
        set_times = self.ui.timeLine.set_time_slider(self.point_list)
        self.ui.time_slider.setRange(0, set_times[2])
        tc = TimeConverter()
        from_time = tc.get_time_hrs_mins(set_times[0])
        self.ui.from_display.setText(from_time)
        self.ui.from_display.setAlignment(Qt.Qt.AlignCenter)
        to_time = tc.get_time_hrs_mins(set_times[1])
        self.ui.to_display.setText(to_time)
        self.ui.to_display.setAlignment(Qt.Qt.AlignCenter)

    def get_curr_time(self, time):
        """Displays time slider current value"""
        display = self.ui.timeLine.get_curr_time(time, self.point_list)
        self.ui.time_display.setText(display)
        self.ui.time_display.setAlignment(Qt.Qt.AlignCenter)



if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MainWindow()
    myapp.show()
    sys.exit(app.exec_())
