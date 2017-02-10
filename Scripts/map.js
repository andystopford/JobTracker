
var map = L.map('map').setView([51.1595954895, 0.260109901428], 13);
L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
        '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>'}).addTo(map);

L.control.scale().addTo(map);

if(typeof MainWindow != 'undefined') {
    var onMapMove = function() { MainWindow.onMapMove(map.getCenter().lat, map.getCenter().lng) ;}
    map.on('move', onMapMove);
    onMapMove();
}

// Draw track from GPS points
var track = L.polyline({color: 'red'});

function add_track(latlngs) {
    track.addTo(map);
    track.setLatLngs([latlngs]);
    track.setStyle({color: '#4E47AB', dashArray: '5, 10', weight: 2});
    }

function del_track() {
    map.removeLayer(track);
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