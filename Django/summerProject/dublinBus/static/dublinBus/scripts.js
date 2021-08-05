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

async function displayRoute(directionsService, directionsRenderer, markersArray, routeNumberAndDir) {
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

    // Make a new bounds object with the coordinates of markersOnRoute which will ensure all the markers are shown
    var bounds = new google.maps.LatLngBounds();
    for (var i = 0; i < markersOnRoute.length; i++) {
        bounds.extend(markersOnRoute[i].getPosition());
    }
    map.fitBounds(bounds);
    try {
        // Make request to get the next departure time for this route from the timetable
        let res = await fetch(`/get_next_bus_time/${routeNumberAndDir}`);
        let data = await res.json();
        // Pull the departure time and coordinates for start and end stops on the route from the response
        let departure_time = data['time'];
        let route_start_end_coords = data['coords'];
        console.log("unformatted departure time:", departure_time);
        // Convert the time from 24hr to a Date object
        let dep_time_hrs = parseInt(departure_time.split(":")[0]);
        let dep_time_mins = parseInt(departure_time.split(":")[1]);
        let date_obj = new Date();
        date_obj.setHours(dep_time_hrs);
        date_obj.setMinutes(dep_time_mins - 5);
        console.log("formatted departure time:", date_obj);

        // Extract the start and end coords
        let start_coords = route_start_end_coords[0];
        let start_lat = start_coords['lat'];
        let start_lon = start_coords['lon'];
        let end_coords = route_start_end_coords[1];
        let end_lat = end_coords['lat'];
        let end_lon = end_coords['lon'];

        let start_coords_formatted = new google.maps.LatLng(start_lat, start_lon);
        let end_coords_formatted = new google.maps.LatLng(end_lat, end_lon);
        // Make the request for directions and display it
        var request = {
            // We'll need to adjust this so the co-ordinates aren't hard-coded and are for start and end points of a route
            origin: start_coords_formatted,
            destination: end_coords_formatted,
            travelMode: "TRANSIT",
            transitOptions: {
                modes: ["BUS"],
                departureTime: date_obj,
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
                                if (current_step.transit.line.short_name === routeNumberAndDir.split(":")[0]) {
                                    console.log("56A found")
                                    directionsRenderer.setDirections(response);
                                    directionsRenderer.setRouteIndex(i);
                                    // Hide all markers except those in our new array which are on our route
                                    showCertainMarkers(markersArray, markersOnRoute);
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
                //directionsRenderer.setDirections(response);
            } else {
                alert("Error with response from google directions API")
            }
        });
    } catch (err) {
        // If we couldn't display the route and markers then just display the markers
        showCertainMarkers(markersArray, markersOnRoute);
        console.log("Error displaying route for this map from directions api. Err code:", err)

    }

}

function displayStop(markersArray, stopNumber, directionsRenderer) {
    console.log("In displayStop, stopNumber is", stopNumber)
    console.log("In displayStop, markers array is", markersArray)
    let map = markersArray[0].getMap();
    // Close all info windows and hide markers
    showCertainMarkers(markersArray, []);
    // First we want to remove any directions from the directions api from the map
    directionsRenderer.set('directions', null);
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
    } else {
        stopsSelector = document.getElementById("stops");
    }
    for (id in stopsData) {
        let stopOption = document.createElement("option");
        stopOption.value = id;
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
    } else {
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
                route_option.value = current_route.route_short_name.toUpperCase() + ": " + current_direction[0];
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
    userLat;
    userLon;
    usingUserInput; // Boolean for whether the start location is the users geolocation or manually entered
    clickedToSearch; // Boolean for whether the button was clicked to give the route instead of just searching after selecting a prediction

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
        const destinationAutocomplete = new google.maps.places.Autocomplete(destinationInput);
        // Specify just the place data fields that you need.
        destinationAutocomplete.setFields(["place_id"]);
        this.usingUserInput = false;
        this.clickedToSearch = false;

        this.setupPlaceChangedListener(originAutocomplete, "ORIG");
        this.setupPlaceChangedListener(destinationAutocomplete, "DEST");
        this.setupUserStartListener();
        // Add event listener to submit button from user to call route
        document.getElementById('user_input_directions_btn').addEventListener('click', () => {
            this.clickedToSearch = true;
            this.route();
        })
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

    setupUserStartListener() {
        document.getElementById('dir_from_user_location').addEventListener('click', () => {
            if (this.usingUserInput) {
                // If user input was previously true then they want to change to false
                // this means we should display the autocomplete search box and change to false
                document.getElementById('origin-input').style.display = "inline-block";
                this.usingUserInput = false;
                // Change the text of the button
                document.getElementById('dir_from_user_location').innerHTML = "Use current location"
            } else {
                // If user input was false then they want to change to true so we should hide the autocomplete box
                document.getElementById('origin-input').style.display = "none";
                this.usingUserInput = true;
                document.getElementById('dir_from_user_location').innerHTML = "Enter start location manually"
            }
        });
    };

    route() {
        // user_start is a boolean to indicate whether the start point was a user location(true) or place id
        const me = this;

        // Get the time selected by the user/automatically generated as current time from the date/time input
        let date = document.getElementById('date_input').value;
        let time = document.getElementById('time_input').value;

        let selectedDateTime = new Date();
        let hours = time.split(":")[0];
        let minutes = time.split(":")[1];
        selectedDateTime.setHours(hours);
        selectedDateTime.setMinutes(minutes);

        let year = date.split("-")[0];
        let month = date.split("-")[1];
        let day = date.split("-")[2];
        selectedDateTime.setFullYear(year);
        selectedDateTime.setMonth(month);
        selectedDateTime.setDate(day);

        // Return early if the relevant fields haven't been filled out yet
        if (this.usingUserInput === false) {
            if (!this.originPlaceId || !this.destinationPlaceId) {
                // If they clicked the button to get results give a message back to the user so they know they need to
                // select one of the suggested locations from the autocomplete
                if (this.clickedToSearch) {
                    alert("Please select a suggested location from the dropdown to get results");
                }
                return;
            }
            // Clear all (if any) markers from the map before continuing with drawing the directions
            showCertainMarkers(this.markersArray, []); // we don't want to show any markers so pass an empty array
            this.directionsService.route(
                {
                    origin: {placeId: this.originPlaceId},
                    destination: {placeId: this.destinationPlaceId},
                    travelMode: "TRANSIT",
                    transitOptions: {
                        modes: ["BUS"],
                        departureTime: selectedDateTime,
                    },
                },
                async (response, status) => {
                    if (status === "OK") {
                        console.log("RESPONSE LOOK HERE:::", response)
                        // Set the directions on the map
                        me.directionsRenderer.setDirections(response);
                        // Get the info we need for our model from the directions response
                        let dir_info = getInfoFromDirections(response, selectedDateTime);
                        let data_for_model = dir_info[0];
                        let trip_info = JSON.parse(dir_info[1]);
                        // Send the relevant data to our backend so it can get model predictions
                        console.log(data_for_model)
                        let prediction_res = await fetch(`get_direction_bus/${data_for_model}`);
                        let prediction_json = await prediction_res.json();
                        let prediction = JSON.parse(prediction_json)
                        // Get the html from this data that we want to show to the user and then display it to them
                        let prediction_html = getPredictionHTML(prediction, trip_info);
                        let results_container = document.getElementById('results_container');
                        results_container.innerHTML = prediction_html;
                        results_container.style.display = "block";
                    } else {
                        alert("Directions request failed due to " + status);
                    }
                }
            );
        } else if (this.usingUserInput === true) {
            console.log("user location button clicked")
            if (navigator.geolocation) {
                if (!this.destinationPlaceId) {
                    // return if they haven't entered a destination yet
                    // If they clicked the button to get results give a message back to the user so they know they need to
                    // select one of the suggested locations from the autocomplete
                    if (this.clickedToSearch) {
                        alert("Please select a suggested location from the dropdown to get results");
                    }
                    return
                }
                // Clear all (if any) markers from the map before continuing with drawing the directions
                showCertainMarkers(this.markersArray, []); // we don't want to show any markers so pass an empty array
                console.log("attempting routing from user location")
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        this.userLat = position.coords.latitude;
                        this.userLon = position.coords.longitude
                        this.directionsService.route(
                            {
                                origin: {lat: this.userLat, lng: this.userLon},
                                destination: {placeId: this.destinationPlaceId},
                                travelMode: "TRANSIT",
                                transitOptions: {
                                    modes: ["BUS"],
                                    departureTime: selectedDateTime,
                                },
                            },
                            async (response, status) => {
                                if (status === "OK") {
                                    console.log("RESPONSE LOOK HERE:::", response)
                                    // Set the directions on the map
                                    me.directionsRenderer.setDirections(response);
                                    let dir_info = getInfoFromDirections(response, selectedDateTime);
                                    let data_for_model = dir_info[0];
                                    let trip_info = JSON.parse(dir_info[1]);
                                    // Send the relevant data to our backend so it can get model predictions
                                    console.log(data_for_model)
                                    let prediction_res = await fetch(`get_direction_bus/${data_for_model}`);
                                    let prediction_json = await prediction_res.json();
                                    let prediction = JSON.parse(prediction_json)
                                    // Get the html from this data that we want to show to the user and then display it to them
                                    let prediction_html = getPredictionHTML(prediction, trip_info);
                                    let results_container = document.getElementById('results_container');
                                    results_container.innerHTML = prediction_html;
                                    results_container.style.display = "block";

                                } else {
                                    window.alert("Directions request failed due to " + status);
                                }
                            }
                        );
                    },
                    () => {
                        handleLocationError(true, map);
                    }
                );
            } else {
                // Browser doesn't support Geolocation
                handleLocationError(false, map);
            }

        }
    }
}

function getPredictionHTML(prediction, trip_info) {
    // first get the number of bus trips that we have in total as we have a prediction for each
    let num_trips = trip_info.length;
    let prediction_html = "<li>";
    // Use the first for loop to get the indexes (index 0 first step, index 1 second step etc.)
    for (let i = 0; i < num_trips; i++) {
        prediction_html += "<ol>";
        // Now loop through the keys from our data returned from backend and get the appropriate
        // index from each of their respective arrays (the value to the key).
        let trip_step = trip_info[i];
        if (trip_step.step_type === "WALKING") {
            prediction_html += trip_step.description + " ---- " + trip_info.duration;
        } else {
            let instructions_string_arr = trip_step.description.split(" ");
            // remove first element from array and convert back to string
            instructions_string_arr = instructions_string_arr.splice(0, 1, prediction.route[i]);
            let instructions_string = instructions_string_arr.join(" ");
            prediction_html += "Get route " + instructions_string + " ---- ";
            // if "gmaps" was returned by backend instead of a time we can use the built in google maps prediction
            if (prediction.arrival_time[i] === "gmaps") {
                prediction_html += trip_info.duration;
            } else {
                // calculate total time taken by step
                let step_time = new Date(prediction.arrival_time[i]) - new Date(prediction.departure_time[i]);
                prediction_html += step_time.getHours() + " " + step_time.getMinutes() + " mins";
            }
        }
        prediction_html += "</ol>";
    }
    prediction_html += "</li>";
    // Get total time of journey
    let time_taken_timestamp = Math.abs(prediction.arrival_time[num_trips -1].getTime() - prediction.departure_time[0].getTime());
    let hours_taken = new Date(time_taken_timestamp).getHours();
    let minutes_taken = new Date(time_taken_timestamp).getMinutes();

    prediction_html += "Total journey should take " + hours_taken + " hours and " + minutes_taken + " minutes";
    return prediction_html
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

function loadDirUserInput() {
    // Function to load necessary event listeners and values into our directions input from user (date/time etc)
    let date_input = document.getElementById('date_input');
    let time_input = document.getElementById('time_input');
    // Set min and max values for date and time inputs
    // get current date and set as min
    let now = new Date();
    let current_date = now.toISOString().split("T")[0]; // https://stackoverflow.com/a/49916376
    date_input.setAttribute("min", current_date);
    date_input.setAttribute("value", current_date);
    // create new date object as five days later and set as max
    let max_date = now;
    max_date.setDate(now.getDay() + 5)
    let max_date_formatted = max_date.toISOString().split("T")[0];
    date_input.setAttribute("max", max_date_formatted);
    console.log(current_date)
    console.log(max_date)
    let hour = now.getHours();
    if (hour < 10) {
        hour = "0" + hour;
    }
    let minutes = now.getMinutes();
    if (minutes < 10) {
        minutes = "0" + minutes;
    }
    let current_time = hour + ":" + minutes;
    console.log(current_time)
    time_input.setAttribute("min", current_time);
    time_input.setAttribute("value", current_time);
}

function getInfoFromDirections(response, selected_date_time) {
    // Function to pull all bus trips returned in a directions response from google maps api
    // Returns data as an object with scheduled departure time, stop number and route number as keys

    // Trip description will hold info from our response not needed for model but for the front end
    // Array of objects with each object being one step of the trip (walking or bus)
    let trip_description = [];

    date_time_string = selected_date_time.toString();
    let data_for_model = {
        "departure_times": [],
        "departure_stops": [],
        "arrival_stops": [],
        "route_names": [],
        "date_time": date_time_string,
    }
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
                    let departure_time = current_step.transit.departure_time.text;
                    let route_num = current_step.transit.line.short_name;
                    let route_headsign = current_step.transit.headsign;
                    let full_route_name = route_num + ": " + route_headsign;
                    let departure_stop = current_step.transit.departure_stop.name
                    let arrival_stop = current_step.transit.arrival_stop.name

                    // save data to object
                    data_for_model.departure_times.push(departure_time);
                    data_for_model.route_names.push(full_route_name);
                    data_for_model.departure_stops.push(departure_stop);
                    data_for_model.arrival_stops.push(arrival_stop)

                    let step_info = {
                        "step_type": current_step.travel_mode,
                        "distance": current_step.distance,
                        "instructions": current_step.instructions,
                        "duration": current_step.duration,
                        "gmaps_prediction": current_step.transit.arrival_time.value,
                    }
                } else {
                    console.log("step is not transit")
                    // save step info with no detail for gmaps prediction as this is only needed for bus times
                    let step_info = {
                        "step_type": current_step.travel_mode,
                        "distance": current_step.distance,
                        "instructions": current_step.instructions,
                        "duration": current_step.duration,
                        "gmaps_prediction": "n/a",
                    }
                }
            }
        }
    }
    console.log(data_for_model);
    // Return our objects
    trip_description_json = JSON.stringify(trip_description);
    let data_for_model_json = JSON.stringify(data_for_model);
    return [data_for_model_json, trip_description_json];
}