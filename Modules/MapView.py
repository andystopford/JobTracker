import sys

import matplotlib.cm as cm
import matplotlib.colors
from PostcodesIO import PostcodeIO
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from mapbox import Directions
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
        self.osm_map = L.tileLayer('http://{s}.tile.openstreetmap.org'
                                      '/{z}/{x}/{y}.png')
        self.terrain_map = L.tileLayer('https://api.mapbox.com'
                                       '/styles/v1/mapbox/outdoors-v10/tiles/'
                                       '256/{z}/{x}/{y}?access_token=pk.'
                                       'eyJ1IjoiYW5keXN0b3BwcyIsImEiOiJjaXUwN2'
                                       'J4anEwMDAxMzNrZTQxeTVpeGx1In0.'
                                       'BqZQL3MpuDI5kPi0LvZhkQ')
        self.sat_map = L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/'
                                   'satellite-v9/tiles/256/{z}/{x}/{y}?'
                                   'access_token=pk.eyJ1IjoiYW5keXN0b3BwcyIs'
                                   'ImEiOiJjaXUwN2J4anEwMDAxMzNrZTQxeTVpeGx1In'
                                   '0.BqZQL3MpuDI5kPi0LvZhkQ')
        self.map_layer_grp = L.layerGroup()
        self.osm_map.addTo(self.map_layer_grp)
        self.map_layer_grp.addTo(self.map)
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

        self.start_end_grp = L.layerGroup()
        self.map.addLayer(self.start_end_grp)

        self.pcode_grp = L.layerGroup()
        self.map.addLayer(self.pcode_grp)

        self.routing_grp = L.layerGroup()
        self.map.addLayer(self.routing_grp)

        self.colour_index = 0
        self.colormap = cm.autumn

        #self.map.moved.connect(self.test2)
        #self.map.zoom.connect(self.test1)
        #self.map.clicked.connect(self.get_clicked)

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

    def add_osm_map(self):
        """Load standard OSM vector map"""
        self.map_layer_grp.clearLayers()
        self.osm_map.addTo(self.map_layer_grp)

    def add_terrain_map(self):
        """Load Mapbox outdoors-v10"""
        self.map_layer_grp.clearLayers()
        self.terrain_map.addTo(self.map_layer_grp)

    def add_sat_map(self):
        """Load Mapbox Satellite images"""
        self.map_layer_grp.clearLayers()
        self.sat_map.addTo(self.map_layer_grp)

    def clear_map(self):
        self.map.removeLayer(self.tracker)
        self.track_layer_grp.clearLayers()
        self.follower_layer_grp.clearLayers()
        self.seg_layer_grp.clearLayers()
        self.start_end_grp.clearLayers()
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

    def marker_calc(self, time, time_events):
        """time_events = list of lat longs"""
        #pairs = [time_events[i:i + 2] for i in range(0, len(time_events), 2)]
        #print(pairs)
        if len(time_events) == 1:
            self.draw_start(time_events[0], time)
        else:
            self.draw_end(time_events[-1])

    def draw_start(self, start, time):
        """Start of work time block"""
        start_lat = start[0]
        start_lon = start[1]
        block = str(self.parent.time_block)
        time = str('<b>' + 'Block' + ' ' + block + ':' + '</b><br>' + time)
        start_marker = L.marker([start_lat, start_lon])
        self.start_end_grp.addLayer(start_marker)

    def draw_end(self, end):
        """End of work time block"""
        end_lat = end[0]
        end_lon = end[1]
        end_marker = L.marker([end_lat, end_lon])
        self.start_end_grp.addLayer(end_marker)

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
            self.routing_grp.clearLayers()
            self.mapbox_routing(go_from, go_to)
        else:
            self.pcode_grp.clearLayers()
            pcode_marker = L.marker(go_from)
            pcode_marker.bindPopup(postcode_from)
            self.pcode_grp.addLayer(pcode_marker)
            #self.map.open_popup()

    def mapbox_routing(self, go_from, go_to):
        """Get route using mapbox service"""
        service = Directions(access_token='pk.eyJ1IjoiYW5keXN0b3BwcyIsImEiO'
                                          'iJjaXUwN2J4anEwMDAxMzNrZTQxeTVpe'
                                          'Gx1In0.BqZQL3MpuDI5kPi0LvZhkQ')
        origin = {'type': 'Feature', 'geometry':
            {'type': 'Point', 'coordinates': [go_from[1], go_from[0]]}}

        destination = {'type': 'Feature', 'geometry':
            {'type': 'Point', 'coordinates': [go_to[1], go_to[0]]}}
        response = service.directions([origin, destination], 'mapbox/driving')
        driving_routes = response.geojson()
        route = driving_routes['features'][0]['geometry']['coordinates']
        route = [list(elem) for elem in route]  # Convert to list of lists:
        track_layer = L.polyline(route, {'color': '#FF00FF'})
        self.routing_grp.addLayer(track_layer)

    def clear_route(self):
        self.pcode_grp.clearLayers()
        self.routing_grp.clearLayers()

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
