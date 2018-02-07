var map = L.map('map').setView([51.1595954895, 0.260109901428], 13);

var vector_map = L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
        '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>'})

var terrain_map = L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/outdoors-v10/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoiYW5keXN0b3BwcyIsImEiOiJjaXUwN2J4anEwMDAxMzNrZTQxeTVpeGx1In0.BqZQL3MpuDI5kPi0LvZhkQ', {
    maxZoom: 18,
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
        '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>'})

var sat_map = L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/satellite-v9/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoiYW5keXN0b3BwcyIsImEiOiJjaXUwN2J4anEwMDAxMzNrZTQxeTVpeGx1In0.BqZQL3MpuDI5kPi0LvZhkQ', {
    maxZoom: 18,
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
        '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>'})

// Add a map layer
function add_osm_map()   {
    map.removeLayer(sat_map)
    map.removeLayer(terrain_map)
    vector_map.addTo(map);
    }

function add_terr_map() {
    map.removeLayer(sat_map)
    map.removeLayer(vector_map)
    terrain_map.addTo(map);
    }

function add_sat() {
    map.removeLayer(vector_map)
    map.removeLayer(terrain_map)
    sat_map.addTo(map);
    }

// Add scale display
L.control.scale().addTo(map);

// Add in a crosshair for the map (from bboxfinder.com)
var crosshairIcon = L.icon({
    iconUrl: '/home/andy/Projects/Programming/Python/JobTracker2/Icons/crosshair.svg',
    iconSize:     [20, 20], // size of the icon
    iconAnchor:   [10, 10], // point of the icon which will correspond to marker's location
    });
crosshair = new L.marker(map.getCenter(), {icon: crosshairIcon, clickable:false});
crosshair.addTo(map);
// Move the crosshair to the center of the map when the user pans
map.on('move', function() {
    crosshair.setLatLng(map.getCenter());
    });

// Get map centre for display read-out
if(typeof MainWindow != 'undefined') {
    var onMapMove = function() { MainWindow.onMapMove(map.getCenter().lat, map.getCenter().lng) ;}
    map.on('move', onMapMove);
    onMapMove();
    }

///////////////////////////////////////////////////////////////////////////////
// Routing
var routeControl = L.Routing.control(  {
    routeWhileDragging: true,
    units: 'imperial',
    collapsible: true,
    //geocoder: L.Control.Geocoder.nominatim()
    //router: L.Routing.mapbox('pk.eyJ1IjoiYW5keXN0b3BwcyIsImEiOiJjaXUwN2J4anEwMDAxMzNrZTQxeTVpeGx1In0.BqZQL3MpuDI5kPi0LvZhkQ'),
    geocoder: L.Control.Geocoder.photon()
    })
    .addTo(map);

function route(from, to) {
    routeControl.setWaypoints( [
    L.latLng(from),
    L.latLng(to)
    ]);
    }

function hide_ctrl() {
    routeControl.hide();
    }

function show_ctrl() {
    routeControl.show();
    }

function clear_route() {
    routeControl.getPlan().setWaypoints([]);
    }

//Pick route
/*
function createButton(label, container) {
    var btn = L.DomUtil.create('button', '', container);
    btn.setAttribute('type', 'button');
    btn.innerHTML = label;
    return btn;
    }

function createButton(label, container) {
    var btn = L.DomUtil.create('button', '', container);
    btn.setAttribute('type', 'button');
    btn.innerHTML = label;
    return btn;
    }

map.on('click', function(e) {
    var container = L.DomUtil.create('div'),
        startBtn = createButton('Start from this location', container),
        destBtn = createButton('Go to this location', container);
    L.popup()
        .setContent(container)
        .setLatLng(e.latlng)
        .openOn(map);
    L.DomEvent.on(startBtn, 'click', function() {
        //MainWindow.map_clicked(e.latlng);
        //alert('adding')
        routing.spliceWaypoints(0, 1, e.latlng);
        map.closePopup();
        });
    L.DomEvent.on(destBtn, 'click', function() {
        routing.spliceWaypoints(routing.getWaypoints().length - 1, 1, e.latlng);
        map.closePopup();
        });
    });

var ReversablePlan = L.Routing.Plan.extend({
    createGeocoders: function() {
        var container = L.Routing.Plan.prototype.createGeocoders.call(this),
            reverseButton = createButton('↑↓', container);
            L.DomEvent.on(reverseButton, 'click', function()
             { var waypoints = this.getWaypoints();
             this.setWaypoints(waypoints.reverse());
             }, this);
        return container;
    }
});

var plan = new ReversablePlan([
        L.latLng(57.74, 11.94),
        L.latLng(57.6792, 11.949)
    ], {
        geocoder: L.Control.Geocoder.nominatim(),
        routeWhileDragging: true
    }),
    control = L.Routing.control({
        routeWhileDragging: true,
        plan: plan
    }).addTo(map);
*/
///////////////////////////////////////////////////////////////////////////////
// Draw track from GPS points
var track_layer_grp = L.layerGroup().addTo(map);

function add_track(latlngs, colour) {
    track_layer = L.polyline({color: 'red'})
    track_layer.setLatLngs([latlngs])
    track_layer.setStyle({color: colour, dashArray: '5, 10', weight: 2})
    track_layer_grp.addLayer(track_layer)
    }

function clear_tracks() {
    track_layer_grp.clearLayers()
    }

// Draw waypoints
var waypoint_grp  = L.layerGroup().addTo(map);

function add_waypoint(latlng, colour) {
    waypoint_layer = L.circle()
    waypoint_layer.setLatLng(latlng)
    waypoint_layer.setRadius(20)
    waypoint_layer.setStyle({color: colour})
    waypoint_grp.addLayer(waypoint_layer)
    }

function clear_waypoints() {
    waypoint_grp.clearLayers()
    }

////////////////////////////////////////////////////////////
// Layer group for start/finish markers
var grp = L.layerGroup().addTo(map);

//function add_layer_grp() {
    //grp = L.layerGroup().addTo(map); // implicit global
    //grp.addLayer(start_layer);
    //}

function clear_layer_grp() {
    grp.clearLayers()
    }

 // draw a marker to follow the track
var tracker = L.marker();

function draw_tracker(lat, lng) {
    tracker.addTo(map);
    tracker.setLatLng([lat, lng]);
    }

function center_on_marker() {
    // zoom on tracker
    var latLngs = [tracker.getLatLng()];
    var markerBounds = L.latLngBounds(latLngs);
    map.fitBounds(markerBounds);
    }

function move(lat, lng) {
    tracker.setLatLng([lat, lng]);
    }

///////////////////////////////////////////////////////////
// Segments
function add_segment(latlngs, colour) {
    segment_layer = L.polyline({color: '000000'});
    grp.addLayer(segment_layer)
    segment_layer.setLatLngs([latlngs]);
    segment_layer.setStyle({color: colour});
    }
/////////////////////////////////////////////////////////////
// start and end markers
function add_start(lat, lng, time) {
    start_layer = L.marker([lat, lng], {icon: startIcon});
    grp.addLayer(start_layer);
    start_layer.bindPopup(time).openPopup();
    ;}

var endIcon = new L.Icon({
      iconUrl: '/home/andy/Projects/Programming/Python/JobTracker2/Icons/icon_end.png', shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [1, -34],
      shadowSize: [41, 41]
});

function add_end(lat, lng) {
    end_layer = L.marker([lat, lng], {icon: endIcon});
    grp.addLayer(end_layer)
    ;}

function del_end() {
    map.removeLayer(end_layer);
    }

var startIcon = new L.Icon({
  iconUrl: '/home/andy/Projects/Programming/Python/JobTracker2/Icons/icon_start.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

////////////////////////////////////////////////////////////////
//Test
function test() {
    var text = String(grp.getLayerId(start_layer));
    var id = grp.getLayerId(start_layer)
    tracker.bindPopup(text).openPopup();
    //grp.clearLayers()
    //grp.removeLayer(id);
    //map.removeLayer(track);
    return id
    }