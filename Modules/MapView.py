import json
import sys

import matplotlib.cm as cm
from PyQt4 import QtCore, QtWebKit

sys.path.append('./Scripts/')
from PostcodesIO import PostcodeIO

class MapView(QtWebKit.QWebView):
    def __init__(self, parent):
        """Displays OpenStreetMap"""
        self.parent = parent
        super(MapView, self).__init__(parent)
        self.page().mainFrame().addToJavaScriptWindowObject("MainWindow", self)
        self.load(QtCore.QUrl('./Scripts/map.html'))
        self.loadFinished.connect(self.load_map)
        self.frame = self.page().mainFrame()
        self.layer_name = 0
        self.colour_index = 0
        self.colormap = cm.autumn
        self.routing_ctrl_hidden = False

    def load_map(self):
        """Load a map from specified provider"""
        with open('./Scripts/map.js', 'r') as f:
            self.frame.evaluateJavaScript(f.read())
            self.frame.evaluateJavaScript('add_osm_map();')
            #self.frame.evaluateJavaScript('nom_router();')
            self.toggle_router()

    def osm_map(self):
        """Load standard OSM vector map"""
        self.frame.evaluateJavaScript('add_osm_map();')

    def terrain_map(self):
        """Load Mapbox outdoors-v10"""
        self.frame.evaluateJavaScript('add_terr_map();')

    def sat_map(self):
        """Load Mapbox Satellite images"""
        self.frame.evaluateJavaScript('add_sat();')


    def clear_map(self):
        """Removes previously drawn tracks and markers"""
        home = [51.1595954895, 0.260109901428]
        self.frame.evaluateJavaScript('clear_tracks();')
        self.frame.evaluateJavaScript('clear_layer_grp();')
        self.frame.evaluateJavaScript('clear_waypoints();')
        self.frame.evaluateJavaScript('move({}, {});'.format(home[0], home[1]))

    def draw_track(self, point_list):
        """Breaks TrackPoint list into overlapping pairs and draws a
        polyline for each pair, coloured from a cmap gradient"""
        pair_list = []
        cmap = self.colormap
        pairs = [point_list[i:i+2] for i in range(0, len(point_list), 1)]
        for pair in pairs:
            # Pairs of TrackPoints
            pair_list.append(pair)
        for i, pair in enumerate(pair_list):
            colour = cmap(i/len(pair_list))
            # Convert to Hex:
            colour = self.convert_colour(colour)
            place_list = []
            for item in pair:
                lat = str(item.get_lat())
                lon = str(item.get_lon())
                place_list.append([lat, lon])
            self.frame.evaluateJavaScript('add_track({}, {});'.
                                          format(place_list, colour))

    def draw_waypoints(self, point_list):
        """Adds a marker to distinguish recorded waypoints from
        the interpolated marker position"""
        cmap = self.colormap
        place_list = []
        for item in point_list:
            lat = str(item.get_lat())
            lon = str(item.get_lon())
            place_list.append([lat, lon])
        for i, posn in enumerate(place_list):
            colour = cmap(i/len(place_list))
            colour = self.convert_colour(colour)
            lat = posn[0]
            lon = posn[1]
            self.frame.evaluateJavaScript('add_waypoint({}, {});'.
                                          format([lat, lon], colour))

    def set_colormap(self, colormap):
        """Colourmaps for graduated colour in tracks"""
        colormap_list = [cm.autumn, cm.brg, cm.hsv, cm.jet]
        self.colormap = colormap_list[colormap]

    def convert_colour(self, colour):
        colour = '#%02x%02x%02x' % (255 * colour[0], 255 * colour[1], 255
                                    * colour[2])
        colour = str(colour)
        colour = ' " ' + colour + ' " '
        return colour

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

    def add_segment(self, leg_points, col=None):
        place_list = []
        colour_list = ['#fda07f', '#cd82f2', '#7fd4fd', '#8bf282', '#fde083']
        if not col:
            curr_colour = colour_list[self.colour_index]
        else:
            curr_colour = col
        colour = json.dumps(curr_colour)
        for item in leg_points:
            lat = str(item.get_lat())
            lon = str(item.get_lon())
            place_list.append([lat, lon])
        self.frame.evaluateJavaScript('add_segment({}, {});'.format(place_list,
                                                                    colour))
        if self.colour_index < 4:
            self.colour_index += 1
        else:
            self.colour_index = 0
        return curr_colour

    def draw_start(self, start, time):
        start_lat = start[0]
        start_lon = start[1]
        block = str(self.parent.time_block)
        time = str('<b>' + 'Block' + ' ' + block + ':' + '</b><br>' + time)
        time = json.dumps(time)  # Convert Python string to JS
        self.frame.evaluateJavaScript('add_start({}, {}, {})'.
                                      format(start_lat, start_lon, time))

    def draw_end(self, end):
        end_lat = end[0]
        end_lon = end[1]
        self.frame.evaluateJavaScript('add_end({}, {});'.
                                      format(end_lat, end_lon))

    # Routing
    def route(self):
        """Calculate route between two postcodes"""
        pio = PostcodeIO()
        postcode_from = self.parent.ui.from_box.text()
        go_from = pio.get_latlng(postcode_from)
        if self.parent.ui.to_box.text():
            postcode_to = self.parent.ui.to_box.text()
            go_to = pio.get_latlng(postcode_to)
            self.frame.evaluateJavaScript('remove_pcode_marker();')
            self.frame.evaluateJavaScript('route({}, {});'
                                          .format(go_from, go_to))
        else:
            self.frame.evaluateJavaScript('remove_pcode_marker();')
            self.frame.evaluateJavaScript('draw_pcode_marker({});'
                                          .format(go_from))

    def toggle_router(self):
        """Toggle visibility of routing control on map"""
        if self.routing_ctrl_hidden:
            self.frame.evaluateJavaScript('show_ctrl();')
            self.routing_ctrl_hidden = False
            self.parent.ui.button_rhide.setText("Hide Routing")
        else:
            self.frame.evaluateJavaScript('hide_ctrl();')
            self.routing_ctrl_hidden = True
            self.parent.ui.button_rhide.setText("Show Routing")

    def clear_route(self):
        """Remove route display and markers"""
        self.frame.evaluateJavaScript('clear_route();')
        self.frame.evaluateJavaScript('remove_pcode_marker();')

    def test(self):
        test = self.frame.evaluateJavaScript('test();')
        print(test)

    @QtCore.pyqtSlot(float, float)  # required to make Python method
    # available to JS
    def onMapMove(self, lat, lng):
        self.parent.ui.coord_display.setText('Lng: {:.5f}, Lat: {:.5f}'.
                                             format(lng, lat))

    def panMap(self, lng, lat):
        self.frame.evaluateJavaScript('map.panTo(L.latLng({}, {}));'.
                                      format(lat, lng))

