// function scrapeCW() {
//     //Function to call the current weather scraper
//     fetch('/scrapeCW').then(res => {
//         console.log("CurrentWeather scraper request sent")
//         if (res.status === 200) {
//             console.log("Scraper ran successfully")
//         } else {
//             console.log("scraper failed :(")
//         }
//     })
// }
//
// function scrapeCB() {
//     //Function to call the current bus scraper
//     fetch('/scrapeCB').then(res => {
//         console.log("CurrentBus scraper request sent")
//         if (res.status === 200) {
//             console.log("Scraper ran successfully")
//         } else {
//             console.log("scraper failed :(")
//         }
//     })
// }

function showCertainMarkers(allMarkers, visibleMarkers) {
    // Function that takes all the markers on the map, an array of the markers we want to make visible and
    // the google map object. The function makes only 'visibleMarkers' visible and hides all other markers

    let map = allMarkers[0].getMap();
    // First make all markers invisible
    allMarkers.forEach(current_marker => {
        current_marker.setVisible(false);
        current_marker.infowindow.close(current_marker, map)
    })

    // Now loop over the markers we want to make visible and make only them visible
    visibleMarkers.forEach(current_marker => {
        current_marker.setVisible(true);
    })
}

function displayRoute(directionsService, directionsRenderer, markersArray, routeNumberAndDir) {
    // Function that takes a route number, the map being used and our array of markers as a parameter and
    // Displays directions for that route and only the markers on that route on the map

    // Some logic will be needed here to determine the start and end point co-ordinates of the passed route
    // but for the purposes of the presentation I'm going to hardcode the co-ordinates for route 56A
    console.log("In displayRoute function")
    console.log("Selected route passed through:", routeNumberAndDir)

    // Get the map as it's own variable by accessing it through the first marker in markersArray
    let map = markersArray[0].getMap();
    // First we want to remove any directions from the directions api from the map
    directionsRenderer.set('directions', null);
    // Get array of all the markers in the cluster (all the markers on the map)
    // Create empty array to hold the markers on our route so we can only show them
    let markersOnRoute = [];
    // Loop through all the markers and find those that match our route and add them to our new array
    for (let currentMarker of markersArray) {
        let markerRoutes = []
        currentMarker.routes.forEach(route => {
            markerRoutes.push(route);
        })
        if (markerRoutes.includes(routeNumberAndDir)) {
            markersOnRoute.push(currentMarker);
        }
    }
    // Hide all markers except those in our new array which are on our route
    showCertainMarkers(markersArray, markersOnRoute);
    // Make a new bounds object with the coordinates of markersOnRoute which will ensure all the markers are shown
    var bounds = new google.maps.LatLngBounds();
    for (var i = 0; i < markersOnRoute.length; i++) {
        bounds.extend(markersOnRoute[i].getPosition());
    }
    map.fitBounds(bounds)
}

function displayStop(markersArray, stopNumber) {
    console.log("In displayStop, stopNumber is", stopNumber)
     console.log("In displayStop, markers array is", markersArray)
    let map = markersArray[0].getMap();
    // Close all info windows and hide markers
     showCertainMarkers(markersArray, []);
    // Hide all markers before showing the selected stop;
    for (let marker of markersArray) {
        if (marker.number == stopNumber) {
            console.log("Marker found", marker.number);
            // Make that marker visible
            marker.setVisible(true);
            infoWindow = marker.infowindow;
            infoWindow.open({
                anchor: marker,
                map: map,
                shouldFocus: true,
            });
        }
    }
}

function loadStopsSearch(stopsData) {
    //Function to read in bus stops into a datalist for either the home or user page depending on which page is loaded

    // If the user is looking at the my account page load that datalist, if not load the one on the homepage
    let stopsSelector;
    if (document.URL.includes('myAccount')) {
        stopsSelector = document.getElementById('user_stops');
    }
    else {
        stopsSelector = document.getElementById("stops");
    }
    for (id in stopsData) {
        let currentStop = stopsData[id];
        let stopOption = document.createElement("option");
        let stopNumArr = currentStop.stop_num.split(" ");
        let stopNum = parseInt(stopNumArr[2]);
        stopOption.value = stopNum;
        stopsSelector.appendChild(stopOption);
    }
}

function loadRoutesSearch(routesJson) {
    // Loop through the json data of all routes and add them to our datalist for user selection to either home
    // or user page depending on which page is loaded

    // If the user is looking at the my account page load that datalist, if not load the one on the homepage
    let routes_selector;
    if (document.URL.includes('myAccount')) {
        console.log("in load routes search in my account page")
        routes_selector = document.getElementById("user_routes");
    }
    else {
        console.log("in load routes search not in my account page")
        routes_selector = document.getElementById("routes");
    }
    // First we need to remove all entries in the json file where there is a duplicate route number (route_short_name)
    // there should be two entries for each route number in the json file as they each represent each direction of the route
    // for the purposes of loading the route search we only need to access the data for one direction of each route so
    // we need to effectively half the array before looping through the items and adding them to our search bar

    let entries = []; // array where we will store all the items to be added to the auto search bar
    // first lets get an array of all the values in the json file
    let routesArray = Object.values(routesJson);
    // Code to filter a collection of javascript objects by a certain property adapted from https://stackoverflow.com/a/40784420
    let halvedRoutes = routesArray.filter(function (route) {
        if (!this[route.route_short_name]) {
            this[route.route_short_name] = true;
            return true;
        }
        return false;
    }, Object.create(null));

    for (current_route of halvedRoutes) {
        if (current_route.hasOwnProperty('direction')) {
            // Loop through all the directions the route serves and make them each a separate entry to fill the search bar
            for (current_direction of current_route.direction) {
                let route_option = document.createElement("option");
                route_option.value = current_route.route_short_name.toUpperCase() + ": " + current_direction;
                // route_option.text = current_direction;
                entries.push(route_option);
            }
        }
        // If there are no directions given by the route then we still add it to entry
        else {
            let route_option = document.createElement("option");
            route_option.value = current_route.route_short_name.toUpperCase();
            entries.push(route_option);
        }
        for (let entry of entries) {
            routes_selector.appendChild(entry);
        }
    }
}

function handleLocationError(browserHasGeolocation, map) {
    // Function to handle errors for geolocation
    alert(
        browserHasGeolocation
            ? "Error: The Geolocation service failed and we could not find your location. Please ensure your location is turned on and you have granted location permissions and refresh the page to try again."
            : "Error: Your browser doesn't support geolocation."
    );
}

class AutocompleteDirectionsHandler {
    // Code for AutoCompleteDirectionsHandler adapted from https://developers.google.com/maps/documentation/javascript/examples/places-autocomplete-directions#maps_places_autocomplete_directions-javascript
    map;
    originPlaceId;
    destinationPlaceId;
    directionsService;
    directionsRenderer;
    markersArray;

    constructor(map, markersArray, directionsService, directionsRenderer) {
        this.map = map;
        this.markersArray = markersArray;
        this.originPlaceId = "";
        this.destinationPlaceId = "";
        this.directionsService = directionsService;
        this.directionsRenderer = directionsRenderer;
        this.directionsRenderer.setMap(map);
        const originInput = document.getElementById("origin-input");
        const destinationInput = document.getElementById("destination-input");
        const originAutocomplete = new google.maps.places.Autocomplete(originInput);
        // Specify just the place data fields that you need.
        originAutocomplete.setFields(["place_id"]);
        const destinationAutocomplete = new google.maps.places.Autocomplete(
            destinationInput
        );
        // Specify just the place data fields that you need.
        destinationAutocomplete.setFields(["place_id"]);

        this.setupPlaceChangedListener(originAutocomplete, "ORIG");
        this.setupPlaceChangedListener(destinationAutocomplete, "DEST");
    }

    setupPlaceChangedListener(autocomplete, mode) {
        autocomplete.bindTo("bounds", this.map);
        autocomplete.addListener("place_changed", () => {
            const place = autocomplete.getPlace();

            if (!place.place_id) {
                window.alert("Please select an option from the dropdown list.");
                return;
            }

            if (mode === "ORIG") {
                this.originPlaceId = place.place_id;
            } else {
                this.destinationPlaceId = place.place_id;
            }
            this.route();
        });
    }

    route() {
        if (!this.originPlaceId || !this.destinationPlaceId) {
            return;
        }
        // Clear all (if any) markers from the map before continuing with drawing the directions
        showCertainMarkers(this.markersArray, []); // we don't want to show any markers so pass an empty array
        const me = this;
        this.directionsService.route(
            {
                origin: {placeId: this.originPlaceId},
                destination: {placeId: this.destinationPlaceId},
                travelMode: "TRANSIT",
                transitOptions: {
                    modes: ["BUS"],
                },
            },
            (response, status) => {
                if (status === "OK") {
                    console.log("RESPONSE LOOK HERE:::", response)
                    me.directionsRenderer.setDirections(response);

                } else {
                    window.alert("Directions request failed due to " + status);
                }
            }
        );
    }
}
async function loadRoutes() {
        let routes = await fetch('/get_routes').then(res => {
        return res.json()
    }).then(data => {
        console.log("all routes:", data)
        return data
    });
        return routes
}

async function loadStops() {
        let bus_stop_data = await fetch('/get_bus_stops').then(res => {
        return res.json()
    }).then(data => {
        console.log("bus stop data:", data)
        return data
    });
        return bus_stop_data
}

function loadDataListsHome(bus_stop_data, routes, displaySelectedRoute, displaySelectedStop) {
    // Function to load data into the datalists on the homepage and add event listeners to execute the relevant functions
     // Call the function so the data is loaded in the search bar ready to autocomplete before it's clicked
    loadStopsSearch(bus_stop_data);
    // Call our function to load the route data into the autocomplete search bar here so it's ready to go once the user clicks it
    loadRoutesSearch(routes);
    // Add an event listener to a button so we can call the above function which will then load our directions
    document.getElementById("get_directions").addEventListener("click", displaySelectedRoute);
    document.getElementById("get_stops").addEventListener("click", displaySelectedStop);
    document.getElementById('routes_num').addEventListener('change', displaySelectedRoute);
    document.getElementById('stops_num').addEventListener('change', displaySelectedStop);
}

async function loadDataListsUser() {
    console.log("in load data lists user")
    // Function to load datalists for user page. Currently calling server for bus and stop data again even though
    // we've already loaded them in the homepage which is fairly wasteful and pointless but can't think of another way atm
    let routes = await loadRoutes();
    let stops = await loadStops();
    loadRoutesSearch(routes);
    loadStopsSearch(stops);


}