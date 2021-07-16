function scrapeCW() {
    //Function to call the current weather scraper
    fetch('/scrapeCW').then(res => {
        console.log("CurrentWeather scraper request sent")
        if (res.status === 200) {
            console.log("Scraper ran successfully")
        } else {
            console.log("scraper failed :(")
        }
    })
}

function scrapeCB() {
    //Function to call the current bus scraper
    fetch('/scrapeCB').then(res => {
        console.log("CurrentBus scraper request sent")
        if (res.status === 200) {
            console.log("Scraper ran successfully")
        } else {
            console.log("scraper failed :(")
        }
    })
}

    function showPolyline(map) {
    // Function that takes the map being used and plots a polyline using hard-coded lat & lng

        const flightPlanCoordinates = [
            { lat: 53.3296309426544, lng: -6.24901208670741 },
            { lat: 53.3274927904883, lng: -6.24419027793743 },
            { lat: 53.2813436184493, lng: -6.27720205461647 },
            { lat: 53.2778180682183, lng: -6.28953551909299 },
        ];
        const flightPath = new google.maps.Polyline({
            path: flightPlanCoordinates,
            geodesic: true,
            strokeColor: "#FF0000",
            strokeOpacity: 1.0,
            strokeWeight: 2,
        });
        flightPath.setMap(map);
    }

function showCertainMarkers(allMarkers, visibleMarkers) {
    // Function that takes a cluster object with all the markers on the map, an array of the markers we want to make visible and
    // the google map object. The function makes only 'visibleMarkers' visible and hides all other markers

    // get array of all the markers in markers_cluster (all the markers on the map)
    // allMarkers = markers_cluster.getMarkers();
    // First make all markers invisible
    allMarkers.forEach(current_marker => {
        current_marker.setVisible(false);
        // current_marker.setMap(null);
    })

    // Now loop over the markers we want to make visible and make only them visible
    visibleMarkers.forEach(current_marker => {
        current_marker.setVisible(true);
    })
    // markers_cluster.repaint()
  //    new MarkerClusterer(
  //        map,
  //        visibleMarkers,
  //        { ignoreHidden: true },
  //   {
  //       imagePath: "https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m",
  // });
}
function displayRoute(directionsService, directionsRenderer, markersArray) {
    // Function that takes a route number, the map being used and our array of markers as a parameter and
    // Displays directions for that route and only the markers on that route on the map

    // Some logic will be needed here to determine the start and end point co-ordinates of the passed route
    // but for the purposes of the presentation I'm going to hardcode the co-ordinates for route 56A
    console.log("In displayRoute function")
    // Get array of all the markers in the cluster (all the markers on the map)
    // markersArray = markers_cluster.getMarkers();
    // Create empty array to hold the markers on our route so we can only show them
    markersOnRoute = [];
    // Loop through all the markers and find those that match our route and add them to our new array
    for (let currentMarker of markersArray) {
        if (currentMarker.routes.includes("56A")) {
            markersOnRoute.push(currentMarker);
        }
    }
    // Hide all markers except those in our new array which are on our route
    showCertainMarkers(markersArray, markersOnRoute);

    // Make the request for directions and display it
    var request = {
        // We'll need to adjust this so the co-ordinates aren't hard-coded and are for start and end points of a route
        origin: {lat: 53.3419400535678, lng: -6.23527645441628},
        destination: {lat: 53.2860074546224, lng: -6.37377077680564},
        travelMode: "TRANSIT",
        transitOptions: {
            modes: ["BUS"],
            routingPreference: "FEWER_TRANSFERS",
        },
        provideRouteAlternatives: true,
    };
    directionsService.route(request, function (response, status) {
        console.log(response);
         if (status == 'OK') {
             // Loop through all of the possible route directions given back by the api
             for (let i = 0; i < response.routes.length; i++) {
                 let current_route = response.routes[i];
                 console.count("looping through routes. Current route:", current_route)
                 // Loop through all the legs of the current route
                 for (let j = 0; j < current_route.legs.length; j++) {
                     let current_leg = current_route.legs[j];
                     console.group("current_leg is:", current_leg)
                     // Loop through each step in this leg of the route
                     for (let k = 0; k < current_leg.steps.length; k++) {
                         let current_step = current_leg.steps[k];
                         console.group("current_step is:", current_step)
                         // Check if this step is using public transport and if so check if it's using the correct route
                         if (current_step.travel_mode === "TRANSIT") {
                             console.log("step is in transit")
                             // Check if the bus route is 56A, if it is we know that this route uses 56A at at least some point throughout the route
                             // so we can select the route to be used as the current one in the for loop
                             if (current_step.transit.line.short_name === "56A") {
                                 console.log("56A found")
                                 directionsRenderer.setDirections(response);
                                 directionsRenderer.setRouteIndex(i);
                                 // We want to exit the function now as we've found a match and set the directions,
                                 // so we return to exit all the outer loops
                                 return
                             }
                         } else {
                             console.log("step is not transit")
                         }
                     }
                 }
             }
             // Here we'll just set the default route given by google maps as we could not find a match for the entered route
             console.log("Match could not be found with 56A");
             directionsRenderer.setDirections(response);
         } else {
             alert("Error with response from google directions API")
         }
    });

}
