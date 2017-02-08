import sys
sys.path.append("./Modules")
sys.path.append("./UI")
sys.path.append("./Icons")
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
import qdarkstyle


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_mainWindow()
        self.ui.setup_ui(self)
        self.setWindowTitle("JobTracker 2.0")
        self.setWindowIcon(QtGui.QIcon('./Icons/shackles.png'))
        # self.setStyleSheet(qdarkstyle.load_stylesheet(pyside=False))

        # Signals
        self.ui.button_test.clicked.connect(self.test)
        self.ui.button_back.clicked.connect(self.year_back)
        self.ui.button_forward.clicked.connect(self.year_forward)
        self.ui.button_save.clicked.connect(self.save)
        self.ui.time_slider.valueChanged.connect(self.get_curr_time)
        self.ui.menu_tickets.addAction('Removal', self.add_rem_ticket)
        self.ui.menu_tickets.addAction('Work', self.add_wrk_ticket)
        self.ui.menu_tickets.addAction('Other', self.add_oth_ticket)

        ##################################################
        # Initialise
        self.dateDisplay = DateDisplay(self.ui.yearView)
        self.trackModel = TrackModel(self)
        self.timeLine = TimeLine(self)
        self.table_proxy_model = QtGui.QSortFilterProxyModel()
        self.ui.trackTable.setDragDropMode(QtGui.QAbstractItemView.DragOnly)
        self.ui.ticketNotes.installEventFilter(self)
        self.model_dict = {}
        self.key_list = []  # temp store for model_dict keys
        self.point_list = []
        self.time_posn = ()
        self.dirty = False
        self.time_block = 1  # For map marker popups
        self.selected_indices = []
        today = datetime.date.today()
        self.year = today.year
        self.showMaximized()
        self.startup()

    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.FocusOut and
                source is self.ui.ticketNotes):
            print('eventFilter: focus out')
            self.ui.ticketNotes.save()
        return super(MainWindow, self).eventFilter(source, event)

    def keyPressEvent(self, e):
        if self.ui.mapView.hasFocus() or self.ui.time_slider.hasFocus():
            if e.key() == QtCore.Qt.Key_Control:
                time_events = self.timeLine.mark_time()
                self.display_times(time_events)
            if e.key() == QtCore.Qt.Key_Z:
                self.ui.mapView.zoom_tracker()
        if self.ui.hoursTable.hasFocus():
            if e.key() == QtCore.Qt.Key_Return:
                self.ui.hoursTable.update_tracks()
        if self.ui.expensesTable.hasFocus():
            if e.key() == QtCore.Qt.Key_Return:
                self.ui.expensesTable.update()

    def startup(self):
        dataIO = DataIO(self)
        dataIO.get_gpx()
        self.table_proxy_model.setSourceModel(self.trackModel)
        self.ui.trackTable.setModel(self.table_proxy_model)
        self.ui.trackTable.set_selection_model(self.trackModel)
        self.ui.trackTable.setSortingEnabled(True)
        self.ui.yearView.setItemDelegate(self.dateDisplay)
        self.init_model()
        self.setup_year(True)
        dataIO.open()

    def init_model(self):
        """Model initialised - called at startup so calendar dates
        can be filled in, and added to model_dict"""
        if self.year not in self.model_dict:
            model = Model(self)
            model.set_year(self.year, True)
            self.model_dict[self.year] = model
        self.model = self.model_dict[self.year]

    def setup_year(self, new_year):
        """Populates dateDisplay"""
        self.ui.yearView.setModel(self.model)
        self.ui.yearView.set_selection_model(self.model)
        self.ui.label_year.setText(str(self.year))
        dataIO = DataIO(self)
        log_list = dataIO.get_logs(self.year)
        date_list = self.model.set_year(self.year, new_year)
        self.dateDisplay.setup(date_list, log_list)

    def year_back(self):
        self.year -= 1
        self.clear_year()

    def year_forward(self):
        self.year += 1
        self.clear_year()

    def clear_year(self):
        self.clear_date()
        self.init_model()
        self.setup_year(False)

    def clear_date(self):
        self.ui.mapView.clear_map()
        self.timeLine.zero_time_list()
        self.trackModel.clear()
        self.ui.from_display.clear()
        self.ui.time_display.clear()
        self.ui.to_display.clear()
        self.ui.jobTickets.clear()
        self.ui.ticketNotes.clear()
        self.ui.hoursTable.clear()
        self.ui.hoursTable.reset()
        self.ui.expensesTable.clear()
        self.ui.expensesTable.reset()
        self.trackModel.reset()
        self.point_list = []
        return

    def get_curr_time(self, time):
        """Displays time slider current value and gets tracker
        coordinates"""
        gpsAnalyser = GpsAnalyser(self)
        display = self.timeLine.get_curr_time(time, self.point_list)
        self.ui.time_display.setText(display[0])
        self.ui.time_display.setAlignment(Qt.Qt.AlignCenter)
        bisect = gpsAnalyser.bisect(display[1], display[2])
        coords = gpsAnalyser.get_coords(bisect[0], bisect[1], bisect[2])
        posn = gpsAnalyser.find_posn(coords)
        self.ui.mapView.draw_tracker(posn)
        self.timeLine.time_posn = (posn[0], posn[1])

    def select_date(self, indices):
        index = indices[0]
        day = self.model.itemFromIndex(index)
        #if day.child(0, 0) is not None:
        date = day.child(0, 0).data()  # QDate, e.g. (2016, 7, 15)
        self.ui.date_display.setText(date.toString())
        self.clear_date()
        # Colour in tickets:
        self.model.set_year(self.year, False)
        self.selected_indices = indices
        self.timeLine.zero_time_list()
        self.get_track(date)
        self.display_tickets()

    def get_track(self, date):
        """Gets GPS data for selected day and displays it"""
        date = date.toString(1)
        date = date.replace('-', '')
        gpsAnalyser = GpsAnalyser(self)
        self.point_list = gpsAnalyser.get_data(date)
        self.ui.mapView.draw_track(self.point_list)
        set_times = self.timeLine.set_time_slider(self.point_list)
        self.ui.time_slider.setRange(0, set_times[2])
        tc = TimeConverter()
        from_time = tc.get_time_hrs_mins(set_times[0])
        self.ui.from_display.setText(from_time)
        self.ui.from_display.setAlignment(Qt.Qt.AlignCenter)
        to_time = tc.get_time_hrs_mins(set_times[1])
        self.ui.to_display.setText(to_time)
        self.ui.to_display.setAlignment(Qt.Qt.AlignCenter)

    def display_times(self, time_events):
        self.ui.mapView.marker_calc(time_events[0], time_events[3])
        # If we have a start and finish time:
        if len(time_events[3]) == 2:
            self.add_times(time_events)

    def add_times(self, time_events):
        """Displays selected track segment in self.ui.trackTable"""
        segment = self.track_segment(time_events[4], time_events[5])
        leg_points = segment[0]
        miles = self.segment_dist(leg_points)
        miles = round(miles, 2)
        miles = str(miles)
        start = time_events[0]
        end = time_events[1]
        hours = time_events[2]
        time_list = [start, end, hours, miles]
        for i, item in enumerate(time_list):
            time_list[i] = QtGui.QStandardItem(item)
        self.trackModel.appendRow(time_list)
        self.trackModel.setHorizontalHeaderLabels(['Start', 'End', 'Hours', 'Miles'])
        self.time_block += 1
        self.colour_cells(segment[1])

    def get_day(self):
        """Gets the currently selected day from the model"""
        model = self.model_dict[self.year]
        indices = self.selected_indices
        row = indices[0].row()
        col = indices[0].column()
        return model, row, col

    def add_rem_ticket(self):
        day = self.get_day()
        # Adds a ticket to the model for this day
        day[0].add_ticket(day[1], day[2], 'Removal')
        self.display_tickets()
        self.dirty = True

    def add_wrk_ticket(self):
        day = self.get_day()
        day[0].add_ticket(day[1], day[2], 'Work')
        self.display_tickets()
        self.dirty = True

    def add_oth_ticket(self):
        day = self.get_day()
        day[0].add_ticket(day[1], day[2], 'Other')
        self.display_tickets()
        self.dirty = True

    def display_tickets(self):
        """Display tickets in jobTickets list widget"""
        day = self.get_day()
        ticket_list = day[0].get_ticket_list(day[1], day[2])
        self.ui.jobTickets.clear()
        for ticket in ticket_list:
            pos = self.ui.jobTickets.count() + 1
            ticket_name = QtGui.QListWidgetItem()
            ticket_name.setText(ticket.get_name())
            if ticket.get_cat() == 'Removal':
                colour = QtGui.QColor(117, 119, 255)
                ticket_name.setBackgroundColor(colour)
            elif ticket.get_cat() == 'Work':
                colour = QtGui.QColor(255, 224, 128)
                ticket_name.setBackgroundColor(colour)
            else:
                colour = QtGui.QColor(126, 232, 116)
                ticket_name.setBackgroundColor(colour)
            self.ui.jobTickets.insertItem(pos, ticket_name)
        # Select last ticket added
        if len(ticket_list) == 1:
            self.ui.jobTickets.setCurrentItem(ticket_name)
            self.ui.jobTickets.setItemSelected(ticket_name, True)
            self.ui.jobTickets.select_ticket()
        if len(ticket_list) > 1:
            self.ui.jobTickets.setCurrentItem(ticket_name)
            self.ui.jobTickets.setItemSelected(ticket_name, True)
            self.ui.jobTickets.select_ticket()

    # GPS Tracks ##############################################
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
        col = QtGui.QColor()
        col.setNamedColor(colour)
        col.setAlpha(127)
        for i in range(4):
            cell = self.trackModel.item(row, i)
            cell.setBackground(col)

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

    def save(self):
        dataIO = DataIO(self)
        dataIO.save(self.model_dict)
        self.dirty = False

    def test(self):
        return

    def closeEvent(self, event):
        """On closing application window"""
        if self.dirty:
            reply = QtGui.QMessageBox.question(self, "UnSaved Data", "Save ?", \
                                               QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel)
            if reply == QtGui.QMessageBox.Cancel:
                event.ignore()
            elif reply == QtGui.QMessageBox.Yes:
                self.save()
            elif reply == QtGui.QMessageBox.No:
                pass
