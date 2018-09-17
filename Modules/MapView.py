import sys

import matplotlib.cm as cm
import matplotlib.colors
from PostcodesIO import PostcodeIO
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from pyqtlet import L, MapWidget

sys.path.append('./Scripts/')


class MapView(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        """Displays OpenStreetMap"""
        self.parent = parent
        self.mapWidget = MapWidget()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.mapWidget)
        self.setLayout(self.layout)
        self.map = L.map(self.mapWidget)
        self.home = [51.1595954895, 0.260109901428]
        self.map.setView(self.home, 13)
        self.vector_map = L.tileLayer('http://{s}.tile.openstreetmap.org'
                                      '/{z}/{x}/{y}.png')
        self.vector_map.addTo(self.map)
        self.show()

        self.cross_hairs = L.circleMarker(self.home, 10)
        self.cross_hairs.addTo(self.map)

        self.track_layer_grp = L.layerGroup()
        self.map.addLayer(self.track_layer_grp)

        self.follower_layer_grp = L.layerGroup()
        self.map.addLayer(self.follower_layer_grp)

        self.tracker_name = ''
        self.tracker = L.marker(self.home)

        self.seg_layer_grp = L.layerGroup()
        self.map.addLayer(self.seg_layer_grp)

        self.pcode_grp = L.layerGroup()
        self.map.addLayer(self.pcode_grp)

        self.route_ctrl = L.routing()
        self.map.addLayer(self.route_ctrl)

        self.colour_index = 0
        self.colormap = cm.autumn

        #self.map.moved.connect(self.test2)
        self.map.zoom.connect(self.test1)
        self.map.clicked.connect(self.get_clicked)

    def test(self, event):
        print(event)
        self.map.getState(self.get_state)

    def get_state(self, e):
        """Gets map state"""
        print(e)

    def test1(self, e):
        print(e['type'].toString())

    def test2(self, e):
        """Get the name of the pyqt signal e.g. 'Moved' """
        mov = list(e.values())
        for obj in mov:
            print('obj', obj.toString())
        print(mov)

    def test3(self, e):
        print('test3', e)

    def get_clicked(self, event):
        """Get latlng from clicked point"""
        # Extract QJsonValue object with key 'latlng'
        latlng = event['latlng']
        # Get the dictionary containing keys 'lat' and 'lng'
        latlng = latlng.toVariant()
        print(latlng)

    def clear_map(self):
        self.map.removeLayer(self.tracker)
        self.track_layer_grp.clearLayers()
        self.follower_layer_grp.clearLayers()
        self.map.setView([51.1595954895, 0.260109901428], 13)

    def draw_tracker(self, posn):
        """Draws a tracker
        """
        self.map.removeLayer(self.tracker)
        lat = posn[0]
        lng = posn[1]
        self.tracker = L.marker([lat, lng])
        self.map.addLayer(self.tracker)

    def zoom_tracker(self):
        """Zooms to tracker
        """
        latlng = self.tracker.getLatlng()
        self.map.setView(latlng, 15)

    def draw_track(self, point_list):
        """Breaks TrackPoint list into overlapping pairs and draws a
                polyline for each pair, coloured from a cmap gradient"""
        pair_list = []
        cmap = self.colormap
        pairs = [point_list[i:i + 2] for i in range(0, len(point_list), 1)]
        for pair in pairs:
            # Pairs of TrackPoints
            pair_list.append(pair)
        for i, pair in enumerate(pair_list):
            latlngs = []
            for item in pair:
                lat = str(item.get_lat())
                lon = str(item.get_lon())
                latlngs.append([lat, lon])
            #colour = cmap(i / len(pair_list))
            # Convert to Hex:
            #colour = self.convert_colour(colour)
            track_layer = L.polyline(latlngs, {'color': '#aa82ff'})
            self.track_layer_grp.addLayer(track_layer)

    def draw_waypoints(self, point_list):
        """Adds a marker to distinguish recorded waypoints from
        the interpolated marker position"""
        return

    def get_trail_pairs(self, before_points, after_points):
        """Breaks point lists into pairs and assigns colours for before
        and after trails"""
        self.follower_layer_grp.clearLayers()
        b_pair_list = []
        a_pair_list = []
        #bef_cols = ["#ff7e7e", "red"]
        bef_cols = ["#ffdfdd", "red"]
        aft_cols = ["blue", "#f4f3ff"]
        cmap_before = matplotlib.colors.LinearSegmentedColormap.from_list\
            ("", bef_cols)
        cmap_after = matplotlib.colors.LinearSegmentedColormap.from_list\
            ("", aft_cols)

        b_pairs = [before_points[i:i + 2] for i in
                   range(0, len(before_points), 1)]
        a_pairs = [after_points[i:i + 2] for i in
                   range(0, len(after_points), 1)]
        self.draw_trail(b_pairs, b_pair_list, cmap_before)
        self.draw_trail(a_pairs, a_pair_list, cmap_after)

    def draw_trail(self, pairs, pair_list, cmap):
        """Draw a polyline for before and after trails"""
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
            self.add_solid_track(place_list, colour)

    def add_solid_track(self, latlngs, colour):
        """Adds polyline layers to follower_grp"""
        follower_layer = L.polyline(latlngs, {'color': colour, 'weight': 4})
        self.follower_layer_grp.addLayer(follower_layer)

    def add_segment(self, leg_points, col=None):
        """Adds tracks from previous tickets"""
        colour_list = ['#fda07f', '#cd82f2', '#7fd4fd', '#8bf282', '#fde083']
        if not col:
            curr_colour = colour_list[self.colour_index]
        else:
            curr_colour = col
        latlngs = []
        for item in leg_points:
            lat = str(item.get_lat())
            lon = str(item.get_lon())
            latlngs.append([lat, lon])
        seg_layer = L.polyline(latlngs, {'color': curr_colour})
        self.seg_layer_grp.addLayer(seg_layer)
        if self.colour_index < 4:
            self.colour_index += 1
        else:
            self.colour_index = 0
        return curr_colour

    def route(self):
        """Calculate route between two postcodes"""
        pio = PostcodeIO()
        postcode_from = self.parent.ui.from_box.text()
        go_from = pio.get_latlng(postcode_from)
        if self.parent.ui.to_box.text():
            postcode_to = self.parent.ui.to_box.text()
            go_to = pio.get_latlng(postcode_to)
            self.pcode_grp.clearLayers()
            self.frame.evaluateJavaScript('route({}, {});'
                                          .format(go_from, go_to))
        else:
            self.frame.evaluateJavaScript('remove_pcode_marker();')
            self.frame.evaluateJavaScript('draw_pcode_marker({});'
                                          .format(go_from))

    def toggle_router(self):
        return

    def clear_route(self):
        return

    def set_colormap(self, colormap):
        """Colourmaps for graduated colour in tracks"""
        colormap_list = [cm.autumn, cm.brg, cm.hsv, cm.jet]
        self.colormap = colormap_list[colormap]

    def convert_colour(self, colour):
        """Converts decimal numbers to hex string"""
        colour = '#%02x%02x%02x' % (int(255 * colour[0]), int(255 * colour[1]),
                                    int(255 * colour[2]))
        colour = str(colour)
        return colour
