from GpsAnalyser import *
from PyQt4 import QtGui, QtCore
from TimeConverter import *


class TrackModel(QtGui.QStandardItemModel):
    def __init__(self, parent):
        super(TrackModel, self).__init__(parent)
        """Model to contain track segments selected from map to
        display in trackTable"""
        self.parent = parent
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(['Start', 'End', 'Hours', 'Miles',
                                        'Show'])
        self.itemChanged.connect(self.toggle_row)

    def toggle_row(self, item):
        if item.isCheckable():
            # print('TrackModel: ', item.checkState())
            if item.checkState():
                return
                # print('checked')
            else:
                # print('unchecked')
                self.parent.remove_segment(item.row())

    def reset(self):
        self.setHorizontalHeaderLabels(['Start', 'End', 'Hours', 'Miles',
                                        'Show'])

    def enter_track(self, time_events):
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
        self.appendRow(time_list)
        self.reset()
        self.colour_cells(segment[1])

    def colour_cells(self, colour):
        """Colour rows in TrackTable"""
        row = self.rowCount() - 1
        col = QtGui.QColor()
        col.setNamedColor(colour)
        for i in range(5):
            cell = self.item(row, i)
            cell.setBackground(col)
            cell.setForeground(QtGui.QColor('#1d1e1f'))

    def read_tracks(self):
        """Reads row by row to get list of visible track segments"""
        tc = TimeConverter()
        row_count = self.rowCount()
        for row in range(0, row_count):
            if self.item(row, 4).checkState():
                start = self.item(row, 0).text()
                start = tc.get_time_mins(start)
                end = self.item(row, 1).text()
                end = tc.get_time_mins(end)
                print(start, end)

    def track_segment(self, start, end, col=None):
        """Selects the trackpoints between the specified times and sends
        segment to mapView"""
        leg_points = []
        for point in self.parent.point_list:
            if point.time >= start:
                if point.time <= end:
                    leg_points.append(point)
        if col:
            # Colours of previously saved tracks
            colour = self.parent.ui.mapView.add_segment(leg_points, col)
        else:
            colour = self.parent.ui.mapView.add_segment(leg_points)
        self.read_tracks()
        return leg_points, colour

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