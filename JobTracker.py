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
from TrackModel import*
from DateModel import*


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
        self.ui.button_add_ticket.clicked.connect(self.add_ticket)
        ##################################################
        # Initialise
        self.dateDisplay = DateDisplay(self.ui.yearView)
        self.trackModel = TrackModel(self)
        self.table_proxy_model = QtGui.QSortFilterProxyModel()
        self.dateModel = DateModel(self)
        #self.date_proxy_model = QtGui.QSortFilterProxyModel()
        #self.curr_day = 0
        self.ui.trackTable.setDragDropMode(QtGui.QAbstractItemView.DragOnly)
        #self.ui.dayView.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        #self.ui.job_expenses_table.setModel(self.dateModel)
        #self.ui.job_expenses_table.setColumnHidden(3, True)
        self.model_dict = {}
        self.key_list = []  # temp store for model_dict keys
        self.point_list = []
        self.time_posn = ()
        self.dirty = False
        self.time_block = 1  # For map marker popups
        self.selected_indices = []
        today = datetime.date.today()
        self.year = today.year
        self.startup()

    def startup(self):
        dataIO = DataIO(self)
        dataIO.get_gpx()
        #self.date_proxy_model.setSourceModel(self.dateModel)
        self.table_proxy_model.setSourceModel(self.trackModel)
        self.ui.trackTable.setModel(self.table_proxy_model)
        self.ui.trackTable.set_selection_model(self.trackModel)
        self.ui.dayView.setModel(self.dateModel)
        self.ui.trackTable.setSortingEnabled(True)
        self.ui.yearView.setItemDelegate(self.dateDisplay)
        self.init_model()
        self.setup_year()

    def init_model(self):
        """Model initialised - called at startup so calendar dates
        can be filled in, and added to model_dict"""
        if self.year not in self.model_dict:
            model = Model(self)
            model.set_year(self.year)
            self.model_dict[self.year] = model
        self.model = self.model_dict[self.year]

    def setup_year(self):
        """Populates dateDisplay"""
        self.ui.yearView.setModel(self.model)
        self.ui.yearView.set_selection_model(self.model)
        self.ui.label_year.setText(str(self.year))
        dataIO = DataIO(self)
        log_list = dataIO.get_logs(self.year)
        date_list = self.model.set_year(self.year)
        self.dateDisplay.setup(date_list, log_list)

    def year_back(self):
        self.year -= 1
        self.clear_year()

    def year_forward(self):
        self.year += 1
        self.clear_year()

    def clear_year(self):
        self.ui.mapView.clear_map()
        self.ui.timeLine.zero_time_list()
        self.trackModel.clear()
        self.ui.from_display.clear()
        self.ui.time_display.clear()
        self.ui.to_display.clear()
        self.point_list = []
        self.init_model()
        self.setup_year()

    def get_curr_time(self, time):
        """Displays time slider current value and gets tracker
        coordinates"""
        gpsAnalyser = GpsAnalyser(self)
        display = self.ui.timeLine.get_curr_time(time, self.point_list)
        self.ui.time_display.setText(display[0])
        self.ui.time_display.setAlignment(Qt.Qt.AlignCenter)
        bisect = gpsAnalyser.bisect(display[1], display[2])
        coords = gpsAnalyser.get_coords(bisect[0], bisect[1], bisect[2])
        posn = gpsAnalyser.find_posn(coords)
        self.ui.mapView.draw_tracker(posn)
        self.ui.timeLine.time_posn = (posn[0], posn[1])

    def select_date(self, indices):
        self.selected_indices = indices
        index = indices[0]
        day = self.model.itemFromIndex(index)
        date = day.child(0, 1).data()   # QDate, e.g. (2016, 7, 15)
        self.ui.date_display.setText(date.toString())
        self.ui.timeLine.zero_time_list()
        self.time_block = 1
        self.dateModel.clear()
        self.get_track(date)
        #self.ui.trackTable.clearContents()
        #self.ui.trackTable.setRowCount(0)

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

    def keyPressEvent(self, e):
        if self.ui.mapView.hasFocus() or self.ui.time_slider.hasFocus():
            if e.key() == QtCore.Qt.Key_Enter:
                time_events = self.ui.timeLine.mark_time()
                self.display_times(time_events)
            if e.key() == QtCore.Qt.Key_Z:
                self.ui.mapView.zoom_tracker()

    def display_times(self, time_events):
        self.ui.mapView.marker_calc(time_events[0], time_events[3])
        # If we have a start and finish time:
        if len(time_events[3]) == 2:
            self.add_times(time_events)

    def add_times(self, time_events):
        """Adds time events to the current day's curr_day, and displays
        them in self.ui.trackTable"""
        segment = self.track_segment(time_events[4], time_events[5])
        leg_points = segment[0]
        miles = self.segment_dist(leg_points)
        miles = round(miles, 2)
        miles = str(miles)
        model = self.model_dict[self.year]
        indices = self.selected_indices
        row = indices[0].row()
        col = indices[0].column()
        date = model.item(row, col)
        start = time_events[0]
        end = time_events[1]
        hours = time_events[2]

        # Fill curr_day instance
        #curr_day_item = date.child(0, 2)
        #curr_day = curr_day_item.data()
        #curr_day.add_start_end(start, end, hours, miles)
        #curr_day.append_times(self, segment[1])
        #date_model = curr_day.get_model()
        #self.ui.dayView.setModel(date_model)

        #curr_day.colour_cells(segment[1])
        #self.curr_day = curr_day

        # Fill in trackTable
        time_list = [start, end, hours, miles]
        for i, item in enumerate(time_list):
            time_list[i] = QtGui.QStandardItem(item)

        self.trackModel.appendRow(time_list)
        self.trackModel.setHorizontalHeaderLabels(['Start', 'End', 'Hours', 'Miles'])
        self.time_block += 1
        #self.track_segment(time_events[4], time_events[5])
        self.colour_cells(segment[1])

    def add_ticket(self):
        self.dateModel.add_ticket()

    def track_segment(self, start, end):
        leg_points = []
        for point in self.point_list:
            if point.time >= start:
                if point.time <= end:
                    leg_points.append(point)
        colour = self.ui.mapView.add_segment(leg_points)
        return leg_points, colour

    def colour_cells(self, colour):
        row = self.trackModel.rowCount() -1
        print(row)
        col = QtGui.QColor()
        col.setNamedColor(colour)
        for i in range(4):
            cell = self.trackModel.item(row, i)
            cell.setBackground(col)
        #self.segment_dist(leg_points)


    def segment_dist(self, leg_points):
        gpsAnalyser = GpsAnalyser(self)
        coords = zip(leg_points, leg_points[1:])
        total = 0
        for item in coords:
            bef_lat = item[0].get_lat()
            bef_lon = item[0].get_lon()
            aft_lat = item[1].get_lat()
            aft_lon = item[1].get_lon()
            d = gpsAnalyser.find_posn([bef_lat, bef_lon, aft_lat, aft_lon, 1])
            #print(d[3])
            total += d[3]
        return total


    def test(self):
        return

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MainWindow()
    myapp.show()
    sys.exit(app.exec_())
