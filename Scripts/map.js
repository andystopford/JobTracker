
var map = L.map('map').setView([51.1595954895, 0.260109901428], 13);
L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
        '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>'}).addTo(map);


if(typeof MainWindow != 'undefined') {
    var onMapMove = function() { MainWindow.onMapMove(map.getCenter().lat, map.getCenter().lng) ;}
    map.on('move', onMapMove);
    onMapMove();
}

function move(lat, lng) {
marker.setLatLng([lat, lng]);}

// Draw track from GPS points
var track = L.polyline({color: 'red'});

function add_track(latlngs) {
    track.addTo(map);
    track.setLatLngs([latlngs]);
    }

function del_track() {
    map.removeLayer(track);
    map.removeLayer(start_layer);
    map.removeLayer(end_layer);
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
////////////////////////////////////////////////////////////
// Layer group
//var grp = L.layerGroup().addTo(map);

function add_layer_grp() {
    grp = L.layerGroup().addTo(map); // implicit global
    grp.addLayer(start_layer);
    }

function test() {
    var text = String(grp.getLayerId(start_layer));
    var id = grp.getLayerId(start_layer)
    tracker.bindPopup(text).openPopup();
    //grp.clearLayers()
    //grp.removeLayer(id);
    //map.removeLayer(track);
    return id
    }

/////////////////////////////////////////////////////////////
// start and end markers
function add_start(lat, lng) {
    start_layer = L.marker([lat, lng], {icon: startIcon});
    start_layer.addTo(map)
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
    end_layer.addTo(map)
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
