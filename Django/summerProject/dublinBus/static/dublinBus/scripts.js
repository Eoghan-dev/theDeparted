function scrapeCW() {
    //Function to call the current weather scraper
    fetch('/scrapeCW').then(res => {
        console.log("CurrentWeather scraper request sent")
        if (res.status===200) {
            console.log("Scraper ran successfully")
        }
        else {
            console.log("scraper failed :(")
        }
    })
}
function scrapeCB() {
    //Function to call the current bus scraper
    fetch('/scrapeCB').then(res => {
        console.log("CurrentBus scraper request sent")
        if (res.status===200) {
            console.log("Scraper ran successfully")
        }
        else {
            console.log("scraper failed :(")
        }
    })
}

function showCertainMarkers(allMarkers, visibleMarkers) {
    // Function that takes an array of all the markers on the map, an array of the markers we want to make visible and
    // the google map object. The function makes only 'visibleMarkers' visible and hides all other markers

    // First make all markers invisible
    allMarkers.forEach(current_marker => {
         current_marker.setVisible(false);
       // current_marker.setMap(null);
    })

    // Now loop over the markers we want to make visible and make only them visible
    visibleMarkers.forEach(current_marker => {
         current_marker.setVisible(true);
    })
}

function displayRoute(directionsService, directionsRenderer) {
    // Function that takes a route number, the map being used and our array of markers as a parameter and
    // Displays directions for that route and only the markers on that route on the map

    // Some logic will be needed here to determine the start and end point co-ordinates of the passed route
    // but for the purposes of the presentation I'm going to hardcode the co-ordinates for route 56A
      console.log("In displayRoute function")
      let origin_location = new google.maps.LatLng(53.3419400535678, -6.23527645441628)
      let destination_location = new google.maps.LatLng(53.286105644023, -6.37306211391221)

  var request = {
      origin: {lat :53.3419400535678, lng: -6.23527645441628},
      destination: {lat :53.286105644023, lng: -6.37306211391221},
      travelMode: "TRANSIT"
  };
  directionsService.route(request, function(response, status) {
    if (status == 'OK') {
      directionsRenderer.setDirections(response);
    }
  });
}