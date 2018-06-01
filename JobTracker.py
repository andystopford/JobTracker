######################################################################
# Copyright (C)2017 Andy Stopford
# This is free software: you can redistribute it and/or modify
# under the terms of the GNU General Public License
# as published by the Free Software Foundation; version 2.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# JobTracker version 2.3.1  01/06/18
#######################################################################
import sys
sys.path.append("./Modules")
sys.path.append("./UI")
sys.path.append("./Icons")
from PyQt4 import QtCore, QtGui, Qt
from datetime import date
from UI import Ui_mainWindow
from IO import *
from Model import *
from YearView import *
from MapView import *
from GpsAnalyser import *
from TrackPoint import *
from TimeLine import TimeLine
from DateDisplay import *
from TimeConverter import *
from TrackModel import *
from Explorer import Explorer
import DarkStyle
from Completer import Completer
from Timer import Timer
from WaitingSpinner import QtWaitingSpinner
# from Ticket import Track


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_mainWindow()
        self.ui.setup_ui(self)
        self.setWindowTitle("JobTracker 2.3")
        self.setWindowIcon(QtGui.QIcon('./Icons/shackles.png'))
        self.setStyleSheet(DarkStyle.load_stylesheet())

        ##################################################
        # Initialise
        self.dateDisplay = DateDisplay(self.ui.yearView)
        self.trackModel = TrackModel(self)
        self.timeLine = TimeLine(self)
        self.explorer = Explorer(self)
        self.spinner = QtWaitingSpinner(self.ui.spinner_widget)
        self.timer = Timer(self)
        self.model = None
        self.table_proxy_model = QtGui.QSortFilterProxyModel()
        self.ui.trackTable.setDragDropMode(QtGui.QAbstractItemView.DragOnly)
        self.ui.ticketNotes.installEventFilter(self)
        self.ui.expensesTable.installEventFilter(self)
        self.ui.job_name_box.installEventFilter(self)
        self.ui.paymentTable.installEventFilter(self)
        self.timer_tkt = None
        self.model_dict = {}
        self.key_list = []  # temp store for model_dict keys
        self.point_list = []
        self.dirty = False
        self.time_block = 0  # For identifying track segments
        self.selected_indices = []
        today = date.today()
        self.year = today.year
        self.showMaximized()
        self.startup()

        # Signals
        self.ui.button_explore.clicked.connect(self.explorer.show)
        self.ui.button_back.clicked.connect(self.year_back)
        self.ui.button_forward.clicked.connect(self.year_forward)
        self.ui.button_save.clicked.connect(self.save)
        self.ui.time_slider.valueChanged.connect(self.get_curr_time)
        self.ui.range_slider.rangeChanged.connect(self.set_range)
        self.ui.button_map.toggled.connect \
            (lambda: self.select_map(self.ui.button_map))
        self.ui.button_terrain.toggled.connect \
            (lambda: self.select_map(self.ui.button_terrain))
        self.ui.button_sat.toggled.connect \
            (lambda: self.select_map(self.ui.button_sat))
        self.ui.button_route.clicked.connect(self.ui.mapView.route)
        self.ui.button_rhide.clicked.connect(self.ui.mapView.toggle_router)
        self.ui.button_clear.clicked.connect(self.ui.mapView.clear_route)
        self.ui.menu_track_cols.addAction('Autumn')
        self.ui.menu_track_cols.addAction('BRG')
        self.ui.menu_track_cols.addAction('HSV')
        self.ui.menu_track_cols.addAction('Jet')
        self.ui.menu_track_cols.triggered.connect(self.change_track_cols)
        # self.ui.button_rev_cols.clicked.connect(self.rev_track_cols)
        self.ui.menu_tickets.addAction('Removal', self.add_rem_ticket)
        self.ui.menu_tickets.addAction('Work', self.add_wrk_ticket)
        self.ui.menu_tickets.addAction('Other', self.add_oth_ticket)
        # Timer
        self.ui.button_start_pause.clicked.connect(self.timer.start_timing)
        self.ui.button_apply.clicked.connect(self.timer.apply_timer)
        self.ui.button_clear.clicked.connect(self.timer.clear)
        self.ui.menu_curr_tickets.triggered.connect(self.timer.select_ticket)

    def eventFilter(self, source, event):
        """Detects TicketNotes losing focus and saves its contents to the
        current ticket"""
        if (event.type() == QtCore.QEvent.FocusOut and
                source is self.ui.ticketNotes):
            self.ui.ticketNotes.save()
        if (event.type() == QtCore.QEvent.FocusOut and
                source is self.ui.job_name_box):
            job = self.ui.job_name_box.text()
            self.set_job(job)
        if (event.type() == QtCore.QEvent.FocusOut and
                source is self.ui.paymentTable):
            self.ui.paymentTable.update()
            self.ui.paymentTable.clearSelection()
        return super(MainWindow, self).eventFilter(source, event)

    def keyPressEvent(self, e):
        """Automate data entry/retention in tables and mark start/finish
        times"""
        if self.ui.mapView.hasFocus() or self.ui.time_slider.hasFocus():
            if e.key() == QtCore.Qt.Key_Control:
                time_events = self.timeLine.mark_time()
                self.display_times(time_events)
            if e.key() == QtCore.Qt.Key_Z:
                self.ui.mapView.zoom_tracker()
        if self.ui.hoursTable.hasFocus():
            if e.key() == QtCore.Qt.Key_Return:
                self.ui.hoursTable.update_tracks()
                self.enable_day()
        if self.ui.expensesTable.hasFocus():
            if e.key() == QtCore.Qt.Key_Return:
                self.ui.expensesTable.update()
                self.enable_day()
        if self.ui.paymentTable.hasFocus():
            if e.key() == QtCore.Qt.Key_Return:
                self.ui.paymentTable.update()
        if e.key() == QtCore.Qt.Key_F2:
            self.explorer.show()

    def startup(self):
        """Get GPS data and set up models"""
        dataIO = DataIO(self)
        dataIO.get_gpx()
        self.table_proxy_model.setSourceModel(self.trackModel)
        self.ui.trackTable.setModel(self.table_proxy_model)
        self.ui.trackTable.set_selection_model(self.trackModel)
        self.ui.trackTable.setSortingEnabled(True)
        self.ui.yearView.setItemDelegate(self.dateDisplay)
        self.ui.button_start_pause.setEnabled(False)
        self.init_model()
        self.setup_year(True)
        dataIO.open()

    def disable_day(self):
        """Sets ticket controls disabled until a ticket is
        created/selected"""
        self.ui.job_name_box.setEnabled(False)
        self.ui.ticketNotes.setEnabled(False)
        self.ui.expensesTable.setEnabled(False)
        self.ui.hoursTable.setEnabled(False)
        self.ui.paymentTable.setEnabled(False)

    def enable_day(self):
        """Enables ticket controls when a ticket is selected"""
        self.ui.job_name_box.setEnabled(True)
        self.ui.ticketNotes.setEnabled(True)
        self.ui.expensesTable.setEnabled(True)
        self.ui.hoursTable.setEnabled(True)
        self.ui.paymentTable.setEnabled(True)

    def init_model(self):
        """Model initialised - called at startup so calendar dates
        can be filled in, and added to model_dict"""
        if self.year not in self.model_dict:
            model = Model(self)
            model.set_year(self.year, True)
            self.model_dict[self.year] = model
        self.model = self.model_dict[self.year]

    def setup_year(self, new_year):
        """Sets display of current year"""
        self.ui.yearView.setModel(self.model)
        self.ui.yearView.set_selection_model(self.model)
        self.ui.label_year.setText(str(self.year))
        dataIO = DataIO(self)
        log_list = dataIO.get_logs(self.year)
        date_list = self.model.set_year(self.year, new_year)
        self.dateDisplay.setup(date_list, log_list)
        self.ui.job_name_box.setCompleter(Completer(self))

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
        self.ui.job_name_box.clear()
        self.ui.ticketNotes.clear()
        self.ui.hoursTable.setRowCount(0)
        self.ui.expensesTable.setRowCount(0)
        self.ui.paymentTable.clear()
        self.trackModel.reset()
        self.point_list = []
        self.time_block = 0
        self.disable_day()
        return

    def select_map(self, b):
        """Select displayed map type"""
        if b.text() == 'Map':
            if b.isChecked():
                self.ui.mapView.osm_map()
        if b.text() == 'Terrain':
            if b.isChecked():
                self.ui.mapView.terrain_map()
        if b.text() == 'Satellite':
            if b.isChecked():
                self.ui.mapView.sat_map()

    def set_range(self):
        """Triggered by change of tracker range"""
        time = self.ui.time_slider.value()
        self.get_curr_time(time)

    def get_curr_time(self, time):
        """Displays time slider current value, gets tracker
        coordinates"""
        gpsAnalyser = GpsAnalyser(self)
        display = self.timeLine.get_curr_time(time, self.point_list)
        self.ui.time_display.setText(display[0])
        self.ui.time_display.setAlignment(Qt.Qt.AlignCenter)
        bisect = gpsAnalyser.bisect(display[1], display[2])
        coords = gpsAnalyser.get_coords(bisect[0], bisect[1], bisect[2])
        posn = gpsAnalyser.find_posn(coords)
        # posn = [dest.latitude, dest.longitude, bearing, distance]
        self.ui.mapView.draw_tracker(posn)
        # Set up points for tracker trails
        trail_points = gpsAnalyser.get_trail_points(display[1])
        self.ui.mapView.get_trail_pairs(trail_points[0], trail_points[1])
        self.timeLine.set_time_posn(posn[0], posn[1])

    def select_date(self, indices):
        """Load tickets from selected date"""
        index = indices[0]
        day = self.model.itemFromIndex(index)
        date = day.child(0, 0).data()  # QDate, e.g. (2016, 7, 15)
        self.ui.date_display.setText(date.toString())
        self.clear_date()
        # Colour in tickets:
        self.model.set_year(self.year, False)
        self.selected_indices = indices
        self.timeLine.zero_time_list()
        self.get_track(date)
        self.display_tickets()
        self.ui.jobTickets.clearSelection()
        self.ui.expensesTable.clearSelection()

    def get_track(self, date):
        """Gets GPS data for selected day and displays it"""
        date = date.toString(1)
        date = date.replace('-', '')
        gpsAnalyser = GpsAnalyser(self)
        self.point_list = gpsAnalyser.get_data(date)
        self.ui.mapView.draw_track(self.point_list)
        self.ui.mapView.draw_waypoints(self.point_list)
        set_times = self.timeLine.set_time_slider(self.point_list)
        self.ui.time_slider.setRange(0, set_times[2])
        tc = TimeConverter()
        from_time = tc.get_time_hrs_mins(set_times[0])
        self.ui.from_display.setText(from_time)
        self.ui.from_display.setAlignment(Qt.Qt.AlignCenter)
        to_time = tc.get_time_hrs_mins(set_times[1])
        self.ui.to_display.setText(to_time)
        self.ui.to_display.setAlignment(Qt.Qt.AlignCenter)

    def change_track_cols(self, act):
        """Select colour sequence for displayed track"""
        # track_col = act.text()
        if act.text() == 'Autumn':
            self.ui.mapView.set_colormap(0)
        elif act.text() == 'BRG':
            self.ui.mapView.set_colormap(1)
        elif act.text() == 'HSV':
            self.ui.mapView.set_colormap(2)
        elif act.text() == 'Jet':
            self.ui.mapView.set_colormap(3)
        self.ui.mapView.draw_track(self.point_list)
        self.ui.button_track_cols.setText(act.text())

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
        # Create QStdItems
        for i, item in enumerate(time_list):
            time_list[i] = QtGui.QStandardItem(item)
        chk_box = QtGui.QStandardItem()
        chk_box.setCheckable(True)
        chk_box.setCheckState(QtCore.Qt.Checked)
        time_list.append(chk_box)
        # Append track to model
        self.trackModel.appendRow(time_list)
        self.trackModel.setHorizontalHeaderLabels(['Start', 'End', 'Hours',
                                                   'Miles', 'Show'])
        self.time_block += 1
        self.colour_cells(segment[1])

    def get_day(self):
        """Gets the currently selected day from the model"""
        model = self.model_dict[self.year]
        indices = self.selected_indices
        row = indices[0].row()
        col = indices[0].column()
        # self.ui.ticketNotes.setEnabled(False)
        return model, row, col

    def get_ticket(self):
        day = self.get_day()
        tkt_name = self.ui.jobTickets.currentItem()
        if not tkt_name:
            print('get_ticket() - no ticket selected')
            return
        else:
            tkt_name = tkt_name.text()
            ticket = day[0].get_ticket(day[1], day[2], tkt_name)
            return ticket

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
        text_colour = QtGui.QColor('#1d1e1f')
        if ticket_list:
            for ticket in ticket_list:
                pos = self.ui.jobTickets.count() + 1
                ticket_name = QtGui.QListWidgetItem()
                ticket_name.setText(ticket.get_name())
                ticket_name.setTextColor(text_colour)
                if ticket.get_cat() == 'Removal':
                    colour = QtGui.QColor(140, 142, 255)
                    ticket_name.setBackgroundColor(colour)
                elif ticket.get_cat() == 'Work':
                    colour = QtGui.QColor(253, 160, 127)
                    ticket_name.setBackgroundColor(colour)
                else:
                    colour = QtGui.QColor(172, 209, 158)
                    ticket_name.setBackgroundColor(colour)
                self.ui.jobTickets.insertItem(pos, ticket_name)
            sel = self.ui.jobTickets.item(0)
            self.ui.jobTickets.setCurrentItem(sel)
            self.ui.jobTickets.select_ticket()
            # self.explorer.refresh_today()
            self.timer.fill_menu()

    def set_job(self, job):
        current_ticket = self.get_ticket()
        current_ticket.set_job(job)

    def display_job(self):
        current_ticket = self.get_ticket()
        job = current_ticket.get_job()
        self.ui.job_name_box.setText(job)

    def load_tracks(self):
        """Loads previously saved tracks into mapView"""
        # TODO should be combined with track_segment
        tracks = self.ui.hoursTable.load_tracks()
        for item in tracks:
            track_seg = self.track_segment(item[0], item[1], item[2])
            self.ui.mapView.add_segment(track_seg[0], track_seg[1])

    # GPS Tracks ##############################################

    def track_segment(self, start, end, col=None):
        """Selects the trackpoints between the specified times and sends
        segment to mapView"""
        leg_points = []
        for point in self.point_list:
            if point.time >= start:
                if point.time <= end:
                    leg_points.append(point)
        # Do the next bit elsewhere:
        if col:
            # Colours of previously saved tracks
            colour = self.ui.mapView.add_segment(leg_points, col)
        else:
            colour = self.ui.mapView.add_segment(leg_points)
        return leg_points, colour

    def remove_segment(self, block):
        self.ui.mapView.remove_segment(block)

    def colour_cells(self, colour):
        """Colour rows in TrackTable"""
        row = self.trackModel.rowCount() - 1
        col = QtGui.QColor()
        col.setNamedColor(colour)
        for i in range(5):
            cell = self.trackModel.item(row, i)
            cell.setBackground(col)
            cell.setForeground(QtGui.QColor('#1d1e1f'))

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
            # print(d[3])
            total += d[3]
        return total

    # Save and close ####################################################

    def save(self):
        dataIO = DataIO(self)
        dataIO.save(self.model_dict)
        self.dirty = False

    def closeEvent(self, event):
        """On closing application window"""
        if self.timer.timer_dirty:
            reply = QtGui.QMessageBox.warning(self, "Timer Running",
                                              "Timer Running: Stop and "
                                              "Save?", QtGui.QMessageBox.Yes
                                              | QtGui.QMessageBox.No |
                                              QtGui.QMessageBox.Cancel)
            if reply == QtGui.QMessageBox.Cancel:
                event.ignore()
            elif reply == QtGui.QMessageBox.Yes:
                self.timer.pause()
                self.timer.apply_timer()
                event.ignore()
            elif reply == QtGui.QMessageBox.No:
                if self.dirty:
                    event.ignore()
                else:
                    pass
        elif self.dirty:
            reply = QtGui.QMessageBox.question(self, "UnSaved Data", "Save ?",
                                               QtGui.QMessageBox.Yes |
                                               QtGui.QMessageBox.No |
                                               QtGui.QMessageBox.Cancel)
            if reply == QtGui.QMessageBox.Cancel:
                event.ignore()
            elif reply == QtGui.QMessageBox.Yes:
                self.save()
            elif reply == QtGui.QMessageBox.No:
                pass
