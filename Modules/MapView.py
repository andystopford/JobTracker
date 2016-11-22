from PyQt4 import QtCore, QtGui, QtWebKit
import sys
import json
sys.path.append('./Scripts/')


class MapView(QtWebKit.QWebView):
    def __init__(self, parent):
        self.parent = parent
        super(MapView, self).__init__(parent)
        self.page().mainFrame().addToJavaScriptWindowObject("MainWindow", self)
        self.load(QtCore.QUrl('./Scripts/map.html'))
        self.loadFinished.connect(self.load_map)
        self.frame = self.page().mainFrame()
        self.layer_name = 0
        self.colour_index = 0

    def load_map(self):
        with open('./Scripts/map.js', 'r') as f:
            self.frame.evaluateJavaScript(f.read())

    def clear_map(self):
        home = [51.1595954895, 0.260109901428]
        self.frame.evaluateJavaScript('del_track();')
        self.frame.evaluateJavaScript('clear_layer_grp();')
        self.frame.evaluateJavaScript('move({}, {});'.format(home[0], home[1]))

    def draw_track(self, point_list):
        # a_point = TrackPoint(pointID, time, lat, lon, course)
        self.frame.evaluateJavaScript('del_track();')
        self.frame.evaluateJavaScript('clear_layer_grp();')
        place_list = []
        self.colour_index = 0
        for item in point_list:
            lat = str(item.get_lat())
            lon = str(item.get_lon())
            place_list.append([lat, lon])
        self.frame.evaluateJavaScript('add_track({});'.format(place_list))

    def draw_tracker(self, posn):
        lat = posn[0]
        lon = posn[1]
        self.frame.evaluateJavaScript('draw_tracker({}, {});'.format(lat, lon))

    def zoom_tracker(self):
        self.frame.evaluateJavaScript('center_on_marker();')

    def marker_calc(self, time, time_events):
        """time_events = list of lat longs"""
        #pairs = [time_events[i:i + 2] for i in range(0, len(time_events), 2)]
        #print(pairs)
        if len(time_events) == 1:
            self.draw_start(time_events[0], time)
        else:
            self.draw_end(time_events[-1])

    def draw_start(self, start, time):
        start_lat = start[0]
        start_lon = start[1]
        block = str(self.parent.time_block)
        time = str('<b>' + 'Block' + ' ' + block + ':' + '</b><br>' + time)
        time = json.dumps(time)  # Convert Python string to JS
        self.frame.evaluateJavaScript('add_start({}, {}, {})'.format(start_lat, start_lon, time))
        self.frame.evaluateJavaScript('add_layer_grp();')

    def draw_end(self, end):
        end_lat = end[0]
        end_lon = end[1]
        self.frame.evaluateJavaScript('add_end({}, {});'.format(end_lat, end_lon))

    def add_segment(self, leg_points):
        #self.frame.evaluateJavaScript('del_track();')
        place_list = []
        colour_list = ['#FF4503', '#9F09E8', '#03ACFF', '#1AE809', '#FFC50A']
        #for col, item in enumerate(colour_list):
        #    colour_list[col] = json.dumps(item)
        curr_colour = colour_list[self.colour_index]
        colour = json.dumps(curr_colour)
        for item in leg_points:
            lat = str(item.get_lat())
            lon = str(item.get_lon())
            place_list.append([lat, lon])
        self.frame.evaluateJavaScript('add_segment({}, {});'.format(place_list, colour))
        if self.colour_index < 4:
            self.colour_index += 1
        else:
            self.colour_index = 0
        return curr_colour



    def test(self):
        test = self.frame.evaluateJavaScript('test();')
        print(test)


    @QtCore.pyqtSlot(float, float)  # required to make Python method available to JS
    def onMapMove(self, lat, lng):
        self.parent.ui.coord_display.setText('Lng: {:.5f}, Lat: {:.5f}'.format(lng, lat))

    def panMap(self, lng, lat):
        self.frame.evaluateJavaScript('map.panTo(L.latLng({}, {}));'.format(lat, lng))

