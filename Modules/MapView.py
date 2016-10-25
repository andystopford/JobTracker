from PyQt4 import QtCore, QtGui, QtWebKit
import sys
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

    def load_map(self):
        with open('./Scripts/map.js', 'r') as f:
            self.frame.evaluateJavaScript(f.read())

    def draw_track(self, point_list):
        # a_point = TrackPoint(pointID, time, lat, lon, course)
        self.frame.evaluateJavaScript('del_track();')
        place_list = []
        for item in point_list:
            lat = str(item.get_lat())
            lon = str(item.get_lon())
            place_list.append([lat, lon])
        self.frame.evaluateJavaScript('add_track({});'.format(place_list))

    def draw_tracker(self, lat, lon, bearing):
        self.frame.evaluateJavaScript('draw_tracker({}, {});'.format(lat, lon))

    def zoom_tracker(self):
        self.frame.evaluateJavaScript('center_on_marker();')

    def marker_calc(self, time_events):
        """time_events = list of lat longs"""
        # pairs = [time_events[i:i + 2] for i in range(0, len(time_events), 2)]
        if len(time_events) == 1:
            self.draw_start(time_events[0])
        else:
            self.frame.evaluateJavaScript('del_end();')
            self.draw_end(time_events[-1])

    def draw_start(self, start):
        start_lat = start[0]
        start_lon = start[1]
        self.frame.evaluateJavaScript('add_start({}, {})'.format(start_lat, start_lon))
        self.frame.evaluateJavaScript('add_layer_grp();')

    def draw_end(self, end):
        end_lat = end[0]
        end_lon = end[1]
        self.frame.evaluateJavaScript('add_end({}, {});'.format(end_lat, end_lon))

    def test(self):
        test = self.frame.evaluateJavaScript('test();')
        print(test)


    @QtCore.pyqtSlot(float, float)  # required to make Python method available to JS
    def onMapMove(self, lat, lng):
        self.parent.ui.coord_display.setText('Lng: {:.5f}, Lat: {:.5f}'.format(lng, lat))

    def panMap(self, lng, lat):
        self.frame.evaluateJavaScript('map.panTo(L.latLng({}, {}));'.format(lat, lng))

