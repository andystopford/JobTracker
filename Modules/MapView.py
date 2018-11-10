from collections import OrderedDict

import matplotlib.cm as cm
import matplotlib.colors
from PostcodesIO import PostcodeIO
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from mapbox import Directions
from pyqtlet import L, MapWidget


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

        self.route_layer_grp = L.layerGroup()
        self.map.addLayer(self.route_layer_grp)

        self.colour_index = 0

        self.routing = Routing(self)

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
        markerCallback = MarkerCallback(self, self.tracker)
        markerCallback.get_tracker_latlng()

    def marker_calc(self, time, time_events):
        """time_events = list of lat longs"""
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
        colour_list = ['#7fd4fd', '#8bf282', '#fd8248', '#cd82f2', '#fde083']
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


class Routing:
    """Mapbox routing from pairs of postcodes or picked points. An
    intermediate point 'Via' can be picked."""
    def __init__(self, parent):
        self.parent = parent
        self.home = [51.1595954895, 0.260109901428]
        self.latlng_list = []

        # Set up dictionary of form {layer:object}, e.g. {l1:self.marker_start}
        self.routing_markers = {}
        self.marker_start = L.marker([0, 0], {'draggable': 'true',
                                              'title': 'Start'}, name='Start')
        layer_name = self.marker_start.getLayerName()  # l1
        self.routing_markers[layer_name] = self.marker_start
        self.marker_via = L.marker([0, 0], {'draggable': 'true',
                                            'title': 'Via'}, name='Via')
        self.marker_end = L.marker([0, 0], {'draggable': 'true',
                                            'title': 'End'}, name='End')
        layer_name = self.marker_end.getLayerName()
        self.routing_markers[layer_name] = self.marker_end
        # Create a layer group for the markers and add to the map
        self.routing_marker_grp = L.layerGroup()
        # Add the start and end markers to the markers' layer group
        self.routing_marker_grp.addLayer(self.marker_start)
        self.routing_marker_grp.addLayer(self.marker_end)

        self.parent.map.addLayer(self.routing_marker_grp)

        self.latlng_list = []  # LatLngs of mrkers
        self.enable_pick_via = False
        self.enable_pick_strt = False
        self.enable_pick_end = False
        self.route_vis = True
        self.marker_start.dragend.connect(self.dragged)
        self.marker_end.dragend.connect(self.dragged)
        self.marker_via.dragend.connect(self.recalc_route)

    def postcode_convert(self):
        """Add start and (optionally) end markers to map. If both present
        calls self.recalc_route. n.b. Doesn't allow for picked markers -
        autofill window on pick?"""
        pio = PostcodeIO()
        if self.parent.parent.ui.from_box.text():
            postcode_start = self.parent.parent.ui.from_box.text()
            start = pio.get_latlng(postcode_start)
            self.parent.map.addLayer(self.routing_marker_grp)
            self.marker_start.setLatLng(start)
            if self.parent.parent.ui.to_box.text():
                postcode_end = self.parent.parent.ui.to_box.text()
                end = pio.get_latlng(postcode_end)
                self.marker_end.setLatLng(end)
                self.recalc_route()
                self.parent.parent.ui.button_via.setEnabled(True)

    def dragged(self, event):
        """After dragging Start or End marker instanciates MarkerCallback to
        get the marker postcode from its new LatLng, and display via
        self.display_pcode. The route (if present) is then recalculated."""
        marker = self.routing_markers[event]
        markerCallback = MarkerCallback(self, marker)
        markerCallback.get_latlng()
        self.recalc_route()

    def display_pcode(self, pcode, name):
        """Display current postcode (if any) for dragged marker"""
        if name == 'Start':
            self.parent.parent.ui.from_box.setText(pcode)
        if name == 'End':
            self.parent.parent.ui.to_box.setText(pcode)

    def recalc_route(self):
        """Sends (all) marker latlngs to self.fill_latlng_list callback. At
        end of drag sorts self.routing_markers into correct order (so that mid
        marker is inbetween start and end) """
        self.latlng_list = []
        self.routing_markers = OrderedDict(sorted(self.routing_markers.items()))
        for key in self.routing_markers:
            marker = self.routing_markers[key]
            marker.getLatLng(self.fill_latlng_list)

    def fill_latlng_list(self, callback):
        """Makes a list of marker latlngs"""
        lat = callback['lat']
        lng = callback['lng']
        latlng = [lat, lng]
        self.latlng_list.append(latlng)
        self.test_list()

    def test_list(self):
        """Checks we have all the markers' latlngs and that they have values
        assigned (i.e. not [0, 0]), and if so, sends them to Mapbox for
        routing"""
        num = len(self.routing_marker_grp.layers)
        if len(self.latlng_list) > 1:
            if self.latlng_list[1] != [0, 0]:
                if len(self.latlng_list) == num:
                    self.use_mapbox(self.latlng_list)

    def pick_strt(self):
        self.enable_pick_strt = True

    def pick_end(self):
        self.enable_pick_end = True

    def pick_via(self):
        self.enable_pick_via = True

    def pick_marker(self, event):
        """Moves the enabled marker to the picked position and adds it to
        self.routing_marker_grp"""
        if self.enable_pick_strt:
            layer_name = self.marker_start.getLayerName()
            self.routing_markers[layer_name] = self.marker_start
            latlng = event['latlng']
            lat = latlng['lat']
            lng = latlng['lng']
            latlng = [lat, lng]
            self.marker_start.setLatLng(latlng)
            pio = PostcodeIO()
            postcode = pio.get_postcode(lng, lat)
            self.parent.parent.ui.from_box.setText(postcode)
            self.enable_pick_strt = False
        elif self.enable_pick_end:
            layer_name = self.marker_end.getLayerName()
            self.routing_markers[layer_name] = self.marker_end
            latlng = event['latlng']
            lat = latlng['lat']
            lng = latlng['lng']
            latlng = [lat, lng]
            self.marker_end.setLatLng(latlng)
            self.recalc_route()
            pio = PostcodeIO()
            postcode = pio.get_postcode(lng, lat)
            self.parent.parent.ui.to_box.setText(postcode)
            self.parent.parent.ui.button_via.setEnabled(True)
            self.enable_pick_end = False
        elif self.enable_pick_via:
            layer_name = self.marker_via.getLayerName()
            self.routing_markers[layer_name] = self.marker_via
            latlng = event['latlng']
            lat = latlng['lat']
            lng = latlng['lng']
            latlng = [lat, lng]
            self.marker_via.setLatLng(latlng)
            self.routing_marker_grp.addLayer(self.marker_via)
            self.recalc_route()
            self.enable_pick_via = False
            self.parent.parent.ui.button_via.setEnabled(False)

    def use_mapbox(self, coords):
        """Mapbox routing. n.b. input latlngs need to be reversed """
        rev_coords = []
        for item in coords:
            item = list(reversed(item))
            rev_coords.append(item)
        service = Directions(access_token='pk.eyJ1IjoiYW5keXN0b3BwcyIsImEiO'
                                          'iJjaXUwN2J4anEwMDAxMzNrZTQxeTVpe'
                                          'Gx1In0.BqZQL3MpuDI5kPi0LvZhkQ')
        response = service.directions(rev_coords, 'mapbox/driving',
                                      continue_straight=False)
        driving_routes = response.geojson()
        metres = driving_routes['features'][0]['properties']['distance']
        miles = metres * 0.000621371
        # print('distance', round(miles, 2))
        self.parent.parent.ui.label_miles.setText\
            ('Distance  ' + str(round(miles, 2)) + '  ' + 'Miles')
        route = driving_routes['features'][0]['geometry']['coordinates']
        #print(route)  # A list of tuples
        self.route(route)

    def route(self, route):
        """Draw route"""
        self.parent.route_layer_grp.clearLayers()
        route = [list(elem) for elem in route]  # Convert to list of lists:
        route_layer = L.polyline(route, {'weight': 2, 'color': '#FF00FF',
                                         'smoothFactor': 0.5})
        self.parent.route_layer_grp.addLayer(route_layer)
        route_layer.clicked.connect(self.pick_marker)

    def toggle_route(self):
        """Hides/Shows route"""
        if self.route_vis:
            for layer in self.routing_marker_grp._layers:
                layer.setOpacity(0)
            self.parent.route_layer_grp.clearLayers()
            self.route_vis = False
            self.parent.parent.ui.button_toggle_route.setText('Show')
        else:
            for layer in self.routing_marker_grp._layers:
                layer.setOpacity(1)
            self.recalc_route()
            self.route_vis = True
            self.parent.parent.ui.button_toggle_route.setText('Hide')


class MarkerCallback:
    """Class for handling marker callbacks TODO Needs tidying"""
    def __init__(self, parent, marker):
        self.parent = parent
        self.marker = marker
        self.postcode = ''

    def get_latlng(self):
        self.marker.getLatLng(self.postcode_callback)

    def postcode_callback(self, callback):
        pio = PostcodeIO()
        lat = callback['lat']
        lng = callback['lng']
        self.postcode = pio.get_postcode(lng, lat)
        self.parent.display_pcode(self.postcode, self.marker.name)

    def get_tracker_latlng(self):
        self.marker.getLatLng(self.tracker_callback)

    def tracker_callback(self, callback):
        lat = callback['lat']
        lng = callback['lng']
        self.parent.map.setView([lat, lng], 15)
