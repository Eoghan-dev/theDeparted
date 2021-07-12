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
        // We'll need to adjust this so the co-ordinates aren't hard-coded and are for start and end points of a route
        origin: {lat: 53.3419400535678, lng: -6.23527645441628},
        destination: {lat: 53.2857103566658, lng: -6.37241720059962},
        travelMode: "TRANSIT",
        transitOptions: {
            modes: ["BUS"],
            routingPreference: "FEWER_TRANSFERS",
        },
        provideRouteAlternatives: true,
    };
    directionsService.route(request, function (response, status) {
        console.log(response);

        // Loop through all of the possible route directions given back by the api
        for (let i=0; i<response.routes.length; i++) {
            let current_route = response.routes[i];
           console.log("looping through routes. Current route:", current_route)
            // Loop through all the legs of the current route
            for (let j=0; j<current_route.legs.length; j++) {
                let current_leg = current_route.legs[j];
                console.log("in legs", current_leg);
                // Loop through each step in this leg of the route
                for (let k=0; k<current_leg.steps.length; k++) {
                    let current_step = current_leg.steps[k];
                    console.log("current step:", current_leg.steps[0]);
                    // Check if this step is using public transport and if so check if it's using the correct route
                    if (current_step.travel_mode === "TRANSIT") {
                        // Check if the bus route is 56A, if it is we know that this route uses 56A at at least some point throughout the route
                        // so we can select the route to be used as the current one in the for loop
                        console.log("current route number is", current_step.transit.line.short_name);
                        if (current_step.transit.line.short_name === "56A") {

                            // directionsRenderer.setDirections(response);
                            directionsRenderer.setRouteIndex(i);
                        }
                    } else {
                        console.log("step is not transit")
                    }
                }


            }
        }
        if (status == 'OK') {
            directionsRenderer.setDirections(response);
        }
    });
}