#!/usr/bin/python3.4
import sys
sys.path.append("./Modules")
sys.path.append("./UI")
# sys.path.append("./Scripts")
from PyQt4 import QtCore, QtGui
import datetime
from UI import Ui_MainWindow
from IO import*
from Model import*
from YearView import*
from MapView import*
from GpsAnalyser import*
from TrackPoint import*
from TimeLine import*
from DateDisplay import*


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("JobTracker")

        # Signals
        self.ui.button_test.clicked.connect(self.test)
        self.ui.button_back.clicked.connect(self.year_back)
        self.ui.button_forward.clicked.connect(self.year_forward)
        self.ui.time_slider.valueChanged.connect(self.get_curr_time)
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

    def keyPressEvent(self, e):
        if self.ui.mapView.hasFocus() or self.ui.time_slider.hasFocus():
            if e.key() == QtCore.Qt.Key_Enter:
                time_events = self.ui.timeLine.mark_time()
                self.display_times(time_events)
            if e.key() == QtCore.Qt.Key_Z:
                self.mapView.zoom_tracker()

    def display_times(self, time_events):
        self.ui.start_display.setText(time_events[0])
        self.ui.end_display.setText(time_events[1])
        self.ui.hours_display.setText(time_events[2])
        self.ui.mapView.marker_calc(time_events[3])

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
        date = date.toString(1)
        date = date.replace('-', '')
        gpsAnalyser = GpsAnalyser(self)
        self.point_list = gpsAnalyser.get_data(date)
        self.ui.mapView.draw_track(self.point_list)
        self.ui.timeLine.set_time_slider(self.point_list)

    def get_curr_time(self, time):
        self.ui.timeLine.get_curr_time(time, self.point_list)



if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MainWindow()
    myapp.show()
    sys.exit(app.exec_())
