let map;
let markersArray = [];

function initMap() {
    // load map
  const map = new google.maps.Map(document.getElementById("map"), {
    zoom: 4,
    center: {lat: 53.349804, lng: -6.260310},
  });

}