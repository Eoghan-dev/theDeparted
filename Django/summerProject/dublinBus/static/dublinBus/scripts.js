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
        // Convert the time from 24hr to a Date object
        let dep_time_hrs = parseInt(departure_time.split(":")[0]);
        let dep_time_mins = parseInt(departure_time.split(":")[1]);
        let date_obj = new Date();
        date_obj.setHours(dep_time_hrs);
        date_obj.setMinutes(dep_time_mins - 5);

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
                                // Check if the bus route is 56A, if it is we know that this route uses 56A at at least some point throughout the route
                                // so we can select the route to be used as the current one in the for loop
                                if (current_step.transit.line.short_name === routeNumberAndDir.split(":")[0]) {
                                    directionsRenderer.setDirections(response);
                                    directionsRenderer.setRouteIndex(i);
                                    // Hide all markers except those in our new array which are on our route
                                    showCertainMarkers(markersArray, markersOnRoute);
                                    // We want to exit the function now as we've found a match and set the directions,
                                    // so we return to exit all the outer loops
                                    return
                                }
                            } else {
                            }
                        }
                    }
                }
                // Here we'll just set the default route given by google maps as we could not find a match for the entered route
                //directionsRenderer.setDirections(response);
            } else {
                alert("Error with response from google directions API")
            }
        });
    } catch (err) {
        // If we couldn't display the route and markers then just display the markers
        showCertainMarkers(markersArray, markersOnRoute);

    }

}

async function displayStop(markersArray, stopNumber, directionsRenderer) {
    let map = markersArray[0].getMap();
    // Close all info windows and hide markers
    showCertainMarkers(markersArray, []);
    // First we want to remove any directions from the directions api from the map
    directionsRenderer.set('directions', null);
    // Show spinner
    document.getElementById('stops_spinner').style.display = "block";
    for (let marker of markersArray) {
        if (marker.number == stopNumber) {
            let current_info_window = marker.infowindow;
            // Make a request to our backend to get the next several buses coming to this stop at time of click
            let incoming_buses_res = await fetch(`get_next_four_bus/${stopNumber}`);
            let incoming_buses = await incoming_buses_res.json();
            let previous_info_window_text = current_info_window.getContent();
            // Get the static part of the info window before overwriting it
            let previous_content = previous_info_window_text.split("<h3>")[0];
            let info_window_text = previous_content;
            // Loop over the incoming bus data and each of them to the info window
            let incoming_buses_text = "<h3>Incoming Buses</h3>" + "<ul class='list-group'>";
            for (let route of incoming_buses) {
                let route_name = route[0];
                let minutes_away = route[1];
                if (minutes_away == 0) {
                    incoming_buses_text += `<li class="list-group-item">${route_name} is less than a min away.</li>`;
                } else {
                    incoming_buses_text += `<li class="list-group-item">${route_name} is ${minutes_away} mins away</li>`;
                }
            }
            incoming_buses_text += "</ul></div>";
            info_window_text += incoming_buses_text;
            current_info_window.setContent(info_window_text);
            // Make that marker visible
            marker.setVisible(true);
            current_info_window.open({
                anchor: marker,
                map: map,
                shouldFocus: true,
            });
        }
    }
    document.getElementById('stops_spinner').style.display = "none";
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
        routes_selector = document.getElementById("user_routes");
    } else {
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
        let currentTimestamp = selectedDateTime.getTime();


        let year = date.split("-")[0];
        let month = date.split("-")[1];
        let day = date.split("-")[2];
        selectedDateTime.setFullYear(year);
        selectedDateTime.setMonth(month);
        selectedDateTime.setDate(day);

        let hours = time.split(":")[0];
        let minutes = time.split(":")[1];
        selectedDateTime.setHours(hours);
        selectedDateTime.setMinutes(minutes);

        // CHeck if the user entered date time is older than the current datetime as we don't want to get predictions
        // from the past (can happen if tab was left open)
        if (selectedDateTime.getTime() < currentTimestamp) {
            selectedDateTime = new Date(currentTimestamp);
        }
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
                        // Set the directions on the map
                        me.directionsRenderer.setDirections(response);
                        // Get the info we need for our model from the directions response
                        let dir_info = getInfoFromDirections(response, selectedDateTime);
                        let data_for_model = dir_info[0];
                        let trip_info = dir_info[1];
                        let gmaps_total_journey = dir_info[2];
                        // Send the relevant data to our backend so it can get model predictions
                        let prediction_res = await fetch(`/get_direction_bus/${data_for_model}`);
                        let prediction = await prediction_res.json();

                        // fill in the departure times from trip_info using what was generated in our prediction
                        // loop through trip info starting at the second item as we already have the initial departure time
                        let transit_count = 0;
                        for (let i = 1; i < trip_info.length; i++) {
                            // If it's a walking step we can take the arrival time of the previous transit step as their departure time
                            if (trip_info[i].step_type === "WALKING") {
                                let predicted_departure;
                                let departure_string = "";
                                if (prediction['arrival_time'][transit_count] === "gmaps") {
                                    predicted_departure = trip_info.gmaps_prediction;

                                    departure_string = predicted_departure;
                                } else {
                                    predicted_departure = prediction['arrival_time'][transit_count];
                                    let departure_timestamp = predicted_departure;
                                    departure_string = getGmapsTimeFromTimestamp(departure_timestamp)
                                }

                                trip_info[i].departure_time = departure_string;
                            }
                        }
                        // Get the html from this data that we want to show to the user and then display it to them
                        let prediction_html = getPredictionHTML(prediction, trip_info, gmaps_total_journey);
                        let results_container = document.getElementById('results_container');
                        results_container.innerHTML = prediction_html;
                        results_container.style.display = "block";
                        feather.replace()
                    } else {
                        alert("Directions request failed due to " + status);
                    }
                }
            );
        } else if (this.usingUserInput === true) {
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
                                    // Set the directions on the map
                                    me.directionsRenderer.setDirections(response);
                                    let dir_info = getInfoFromDirections(response, selectedDateTime);
                                    let data_for_model = dir_info[0];
                                    let trip_info = dir_info[1];
                                    let gmaps_total_journey = dir_info[2];
                                    // Send the relevant data to our backend so it can get model predictions
                                    let prediction_res = await fetch(`get_direction_bus/${data_for_model}`);
                                    let prediction = await prediction_res.json();


                                    // fill in the departure times from trip_info using what was generated in our prediction
                                    // loop through trip info starting at the second item as we already have the initial departure time
                                    let transit_count = 0;
                                    for (let i = 1; i < trip_info.length; i++) {
                                        // If it's a walking step we can take the arrival time of the previous transit step as their departure time
                                        if (trip_info[i].step_type === "WALKING") {
                                            let predicted_departure;
                                            let departure_string = "";
                                            if (prediction['arrival_time'][transit_count] === "gmaps") {
                                                predicted_departure = trip_info[i - 1]['departure_time']
                                                departure_string = predicted_departure;
                                            } else {
                                                predicted_departure = prediction['arrival_time'][transit_count];
                                                let departure_timestamp = predicted_departure;
                                                departure_string = getGmapsTimeFromTimestamp(departure_timestamp)
                                            }

                                            trip_info[i].departure_time = departure_string;
                                        }
                                    }

                                    // Get the html from this data that we want to show to the user and then display it to them
                                    let prediction_html = getPredictionHTML(prediction, trip_info, gmaps_total_journey);
                                    let results_container = document.getElementById('results_container');
                                    results_container.innerHTML = prediction_html;
                                    results_container.style.display = "block";
                                    feather.replace()

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

function getDateFromInput() {
        let date = document.getElementById('date_input').value;
        let time = document.getElementById('time_input').value;

        let selectedDateTime = new Date();
        let currentTimestamp = selectedDateTime.getTime();


        let year = date.split("-")[0];
        let month = date.split("-")[1];
        let day = date.split("-")[2];
        selectedDateTime.setFullYear(year);
        selectedDateTime.setMonth(month - 1);
        selectedDateTime.setDate(day);

        let hours = time.split(":")[0];
        let minutes = time.split(":")[1];
        selectedDateTime.setHours(hours);
        selectedDateTime.setMinutes(minutes);
        return selectedDateTime
}

function getGmapsTimeFromTimestamp(timestamp) {
    // function that takes a timestamp and returns it as a formatted 24hr time in the same format as google maps

    let departure_string = "";
    let departure_Date = new Date(timestamp)
    let hour = departure_Date.getHours()
    let minutes = departure_Date.getMinutes()
    if (hour > 12) {
        departure_string += hour - 12 + ":" + minutes + "pm";
    }
    else if (hour === 12)   {
        departure_string += hour + ":" + minutes + "pm";
    }
    else {
        departure_string += hour + ":" + minutes + "am";
    }
    return departure_string
}

function getPredictionHTML(prediction, trip_info, gmaps_total_journey) {
    let initial_departure_time;
    let final_arrival_time
    let total_cost = 0.0;
    // first get the number of bus trips that we have in total as we have a prediction for each
    let num_trips = trip_info.length;
    let prediction_html = "<ul class='list-group'>";
    // Use the first for loop to get the indexes (index 0 first step, index 1 second step etc.)
    let gmaps_journey = false; //boolean for whether we're using gmaps predictions or our own
    let transit_count = 0; //counter to differentiate number of transit steps from walking/transit (i)
    for (let i = 0; i < num_trips; i++) {
        var index = i;
        prediction_html += "<li class='list-group-item'>";
        // Now loop through the keys from our data returned from backend and get the appropriate
        // index from each of their respective arrays (the value to the key).
        let trip_step = trip_info[i];
        // Add time to first item


        if (trip_step.step_type === "WALKING") {

            // First step of journey if walking
            if (i === 0) {
                if (prediction.departure_time[0] === "gmaps") {
                    let gmaps_str = trip_step["departure_time"];
                    initial_departure_time = gmaps_to_timestamp(gmaps_str);
                }
                else {
                    initial_departure_time = Math.abs(parseInt(prediction.departure_time[0]) - parseInt(trip_step.duration.split(" ")[0]) * 1000 * 60);
                }
            }
            prediction_html += trip_step.instructions + " ---- " + trip_step.duration;

        } else {
            // First step of journey if bus
            if (i === 0) {
                if (prediction.departure_time[0] === "gmaps") {
                    let gmaps_str = trip_step["departure_time"];
                    initial_departure_time = gmaps_to_timestamp(gmaps_str);
                }
                else {
                    initial_departure_time = Math.abs(parseInt(prediction.departure_time[0]));
                }
            }
            if (prediction["departure_time"][transit_count] === "gmaps") {
                prediction_html += `<i data-feather="chrome"></i><b>${trip_step.departure_time}: </b>`;
            } else {
                let formatted_date = new Date(prediction["departure_time"][transit_count]);
                let pmboolean = (formatted_date.getHours() >= 12)
                if (formatted_date.getMinutes() < 10) {
                    if (pmboolean === true && formatted_date.getHours() != 12) {
                        formatted_date = (formatted_date.getHours() - 12) + ":0" +formatted_date.getMinutes() + "pm";
                    }
                    else if (pmboolean === true)    {
                        formatted_date = (formatted_date.getHours()) + ":0" +formatted_date.getMinutes() + "pm";
                    }
                    else    {
                        formatted_date = (formatted_date.getHours()) + ":0" +formatted_date.getMinutes() + "am";
                    }
                }
                else {
                    if (pmboolean === true && formatted_date.getHours() != 12) {
                        formatted_date = (formatted_date.getHours() - 12) + ":" +formatted_date.getMinutes() + "pm";
                    }
                    else if (pmboolean === true)    {
                        formatted_date = formatted_date.getHours() + ":" + formatted_date.getMinutes() + "pm";
                    }
                    else    {
                        formatted_date = formatted_date.getHours() + ":" + formatted_date.getMinutes() + "am";
                    }
                }
                prediction_html += `<i data-feather="settings"></i><b>${formatted_date}: </b>`;
            }

            let instructions_string_arr = trip_step.instructions.split(" ");
            // remove first element from array and convert back to string
            instructions_string_arr = instructions_string_arr.slice(1);
            let instructions_string = instructions_string_arr.join(" ");
            prediction_html += "Get route " + trip_step.route_num + " " + instructions_string + " ---- ";
            // if "gmaps" was returned by backend instead of a time we can use the built in google maps prediction
            if (prediction.arrival_time[transit_count] === "gmaps") {
                prediction_html += trip_info[i]["duration"];
                gmaps_journey = true;
            } else {
                // calculate total time taken by step
                let step_time = Math.abs(prediction["arrival_time"][transit_count] - prediction.departure_time[transit_count]);
                prediction_html += ((step_time / 1000) / 60) + " mins ";
            }
            // Get the total number of stops the bus passed for this stop
            let stops_passed = trip_info[i]["num_stops"];
            let fare_status = window.fare_status
            // If the user is logged in but hasn't set a status yet set a default as adult
            if (fare_status.length < 1) {
                fare_status = "adult";
            }
            let leap_card = window.leap_card

            // calculate cost of bus by first calculating whether the current departure time falls within a schooltime range
            let departure_time = trip_info[i].departure_time;
            let schooltime = determineSchoolRange(departure_time);
            // check if route is xpresso (has an x in the route number)
            let xpresso = (trip_step.route_num.includes("x") || trip_step.route_num.includes("X"));
            let fare = calculatePrice(stops_passed, fare_status, leap_card, schooltime, xpresso);
            if (trip_info[i]['agency'] === "Dublin Bus") {
                prediction_html += " ---- €" + fare.toFixed(2);
                total_cost += fare;
            }
            transit_count += 1;
        }
        prediction_html += "</li>";
    }
    if (trip_info[trip_info.length - 1].step_type === "WALKING") {
        if (prediction.arrival_time[prediction.arrival_time.length - 1] === "gmaps") {
                    let gmaps_str = trip_info[trip_info.length-2]["arrival_time"];
                    final_arrival_time = gmaps_to_timestamp(gmaps_str);
                    final_arrival_time += (parseInt(trip_info[trip_info.length-1].duration.split(" ")[0]) * 1000 * 60)
                }
        else {
            final_arrival_time = Math.abs(parseInt(prediction.arrival_time[prediction.arrival_time.length - 1]));
            final_arrival_time += (parseInt(trip_info[trip_info.length-1].duration.split(" ")[0]) * 1000 * 60)
        }
    } else {
        if (prediction.arrival_time[prediction.arrival_time.length - 1] === "gmaps") {
                    let gmaps_str = trip_info[trip_info.length-1]["arrival_time"];
                    final_arrival_time = gmaps_to_timestamp(gmaps_str);
                }
        else {
            final_arrival_time = Math.abs(parseInt(prediction.arrival_time[prediction.arrival_time.length - 1]));
        }
    }
    // Get total time of journey
    let total_time_taken_str = "";
    if (gmaps_journey) {
        // If bus is dublin bus add price, don't otherwise

        // Boolean for whether or not the journey consisted of only dublin bus trips and we should use the fare calculator
        let fareJourney = true;
        trip_info.forEach( trip => {
            if (trip['agency'] != "Dublin Bus") {
                fareJourney = false;
            }
        })
        let total;
        if (fareJourney) {
            total = parseInt(total_journey_time(parseInt(initial_departure_time),parseInt(final_arrival_time)))
            let total_str = "";
            (Math.floor(total/60) === 0) ? total_str = ((total%60) + "mins") : total_str = (Math.floor(total/60) + " hours " + (total%60) + " mins ");
            total_time_taken_str = "<li class='list-group-item list-group-item-primary'>Total journey should take " + total_str + " and should cost €" + total_cost.toFixed(2) + "</li>";
        } else {
            total = parseInt(total_journey_time(parseInt(initial_departure_time),parseInt(final_arrival_time)))
            let total_str = "";
            (Math.floor(total/60) === 0) ? total_str = ((total%60) + "mins") : total_str = (Math.floor(total/60) + " hours " + (total%60) + " mins ");
            total_time_taken_str = "<li class='list-group-item list-group-item-primary'>Total journey should take " + total_str + "</li>";
        }
    } else {
        let time_taken_timestamp = Math.abs(prediction.arrival_time[num_trips - 1] - prediction.departure_time[0]);
        let hours_taken = (time_taken_timestamp / 1000) / 3600;
        let minutes_taken = (time_taken_timestamp / 1000) / 60;

        // Boolean for whether or not the journey consisted of only dublin bus trips and we should use the fare calculator
        let fareJourney = true;
        trip_info.forEach( trip => {
            if (trip['step_type'] === "TRANSIT") {
                if (trip['agency'] != "Dublin Bus") {
                    fareJourney = false;
                }
            }
        });
        if (fareJourney) {
            total = parseInt((final_arrival_time - initial_departure_time) / 1000 / 60);
            let total_str = "";
            (Math.floor(total/60) === 0) ? total_str = ((total%60) + "mins") : total_str = (Math.floor(total/60) + " hours " + (total%60) + " mins ");
            total_time_taken_str = "<li class='list-group-item list-group-item-primary'>Total journey should take " + total_str +" and should cost €" + total_cost.toFixed(2) + "</li>";
        }
        else {
            total = parseInt((final_arrival_time - initial_departure_time) / 1000 / 60);
            let total_str = "";
            (Math.floor(total/60) === 0) ? total_str = ((total%60) + " mins ") : total_str = (Math.floor(total/60) + " hours " + (total%60) + " mins ");
            total_time_taken_str = "<li class='list-group-item list-group-item-primary'>Total journey should take " + total_str + "</li>";
        }
        }

    prediction_html += total_time_taken_str + "</ul>";
    return prediction_html
}
function total_journey_time(initial,final) {
    if (final < initial) {
        final += 86400000;
    }
    let total = (final - initial)/ 1000 / 60;
    return total
}
function gmaps_to_timestamp(gmaps_str) {
    let date_temp = getDateFromInput();
    let converted_time;
    gmaps_str = gmaps_str.split(":");
    if ((gmaps_str[1].includes("am")) ||(gmaps_str[1].includes("AM"))) {
        if (gmaps_str[0] === "12") {
            gmaps_str[0] = "00"
        }
        date_temp.setHours(parseInt(gmaps_str[0]));
        date_temp.setMinutes(parseInt(gmaps_str[1].slice(0,2)))
        converted_time = date_temp.getTime();
    }
    else if ((gmaps_str[1].includes("pm")) ||(gmaps_str[1].includes("PM"))) {
        if (gmaps_str[0] === "12") {
            date_temp.setHours(parseInt(gmaps_str[0]));
        }
        else    {
            date_temp.setHours(parseInt(gmaps_str[0])+12);
        }
        date_temp.setMinutes(parseInt(gmaps_str[1].slice(0,2)))
        converted_time = date_temp.getTime();
    }
    else {
        date_temp.setHours(parseInt(gmaps_str[0]));
        date_temp.setMinutes(parseInt(gmaps_str[1]))
        converted_time = date_temp.getTime();
    }
    return converted_time
}

function determineSchoolRange(departure_time) {
    let valid = false;
    let departure_min;
    // Function to determine if a bus departure time falls within a school range for our fare calculator
    let departure_hour = parseInt(departure_time.split(":")[0]);
    // Parse the departure time minutes differently depending on if response includes pm/am
    if (departure_time.split(":")[1].includes("pm") || departure_time.split(":")[1].includes("am")) {
        departure_min = parseInt(departure_time.split(":")[1].substring(0, 2));
        if (departure_time.split(":")[1].substring(2, 4) === "pm") {
            departure_hour += 12;
        }
    } else {
        departure_min = parseInt(departure_time.split(":")[1])
    }

    let date = new Date();
    // set the departure time to our date object
    date.setHours(departure_hour);
    date.setMinutes(departure_min);
    // get the day of the week (sunday is 0)
    let weekday = date.getDay();
    // valid until 19:00 mon-fri and until 13:30 on saturday. Never valid on sunday
    if (weekday === 7) {
        // If it's before 1pm or after 1pm but before 1.30pm then it's valid
        if ((date.getHours() < 13) || (date.getHours() < 14 && date.getHours() >= 13 && date.getMinutes() < 30)) {
            valid = true;
        }
    } else if (weekday === 0) {
        // Do nothing if it's sunday since it's never valid
    } else {
        // For mon-fri it's valid if it's before 19:00
        if (date.getHours() < 19) {
            valid = true;
        }
    }
    return valid;
}

async function loadRoutes() {
    let routes = await fetch('/get_routes').then(res => {
        return res.json()
    }).then(data => {
        return data
    });
    return routes
}

async function loadStops() {
    let bus_stop_data = await fetch('/get_bus_stops').then(res => {
        return res.json()
    }).then(data => {
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
    let current_day = now.getDate();
    let future_day = current_day + 5;

    max_date.setDate(future_day)
    let max_date_formatted = max_date.toISOString().split("T")[0];
    date_input.setAttribute("max", max_date_formatted);
    let hour = now.getHours();
    if (hour < 10) {
        hour = "0" + hour;
    }
    let minutes = now.getMinutes();
    if (minutes < 10) {
        minutes = "0" + minutes;
    }
    let current_time = hour + ":" + minutes;
    time_input.setAttribute("min", current_time);
    time_input.setAttribute("value", current_time);
}

function getInfoFromDirections(response, selected_date_time) {
    // Function to pull all bus trips returned in a directions response from google maps api
    // Returns data as an object with scheduled departure time, stop number and route number as keys

    // Trip description will hold info from our response not needed for model but for the front end
    // Array of objects with each object being one step of the trip (walking or bus)
    let trip_description = [];
    let gmaps_total_journey_time = "";
    let timestamp = selected_date_time.getTime() / 1000.0;
    let data_for_model = {
        "departure_times": [],
        "departure_stops": [],
        "arrival_stops": [],
        "route_names": [],
        "date_time": timestamp,
    }
    for (let i = 0; i < response.routes.length; i++) {
        let current_route = response.routes[i];
        console.count("looping through routes. Current route:", current_route)
        // Loop through all the legs of the current route
        for (let j = 0; j < current_route.legs.length; j++) {
            let current_leg = current_route.legs[j];
            gmaps_total_journey_time = current_leg.duration.text;
            console.group("current_leg is:", current_leg)
            // Loop through each step in this leg of the route
            for (let k = 0; k < current_leg.steps.length; k++) {
                let current_step = current_leg.steps[k];
                console.group("current_step is:", current_step)
                // Check if this step is using public transport and if so check if it's using the correct route
                let step_info = {}
                if (current_step.travel_mode === "TRANSIT") {
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

                    step_info["step_type"] = current_step.travel_mode;
                    step_info["distance"] = current_step.distance;
                    step_info["instructions"] = current_step.instructions;
                    step_info["duration"] = current_step.duration.text;
                    step_info["gmaps_prediction"] = current_step.transit.arrival_time.value;
                    step_info["arrival_time"] = current_step.transit.arrival_time.text;
                    step_info["departure_time"] = departure_time;
                    step_info["route_num"] = current_step.transit.line.short_name;
                    step_info["num_stops"] = current_step.transit.num_stops;
                    step_info["agency"] = current_step['transit']['line']['agencies'][0]['name'];
                } else {
                    // save step info with no detail for gmaps prediction as this is only needed for bus times
                    step_info["step_type"] = current_step.travel_mode;
                    step_info["distance"] = current_step.distance;
                    step_info["instructions"] = current_step.instructions;
                    step_info["duration"] = current_step.duration.text;
                    step_info["gmaps_prediction"] = "n/a";
                    step_info["arrival_time"] = "n/a";
                    if (k === 0) {
                        step_info["departure_time"] = current_leg.departure_time.text;
                    } else {
                        step_info["departure_time"] = "n/a";
                    }
                    step_info["route_num"] = "n/a";
                    step_info["num_stops"] = "n/a";
                    step_info["agency"] = "n/a";
                }
                trip_description.push(step_info);
            }
        }
    }
    // Return our objects
    let data_for_model_json = JSON.stringify(data_for_model);
    return [data_for_model_json, trip_description, gmaps_total_journey_time];
}

function openCancellationsOverlay() {
    document.getElementById("cancellations_overlay").style.width = "100%";
}

function closeCancellationsOverlay() {
    document.getElementById("cancellations_overlay").style.width = "0%";
}

function fillSidebar(content, type) {
    // takes a parameter of user's fav routes/stops
    let sidebar_content = "";
    if (type === "stops") {

        sidebar_content += "<h3 class='display-1' style='color:rgb(255,193,7)'>Favourite stops</h3>"
        sidebar_content += "<div class='align-items-center'><ul class='list-group'>";
        let content_arr = content.split(",")
        for (let content of content_arr) {
            sidebar_content += `<a href='javascript:closeSidebar()'><li class="list-group-item fav_stops_button_sb" style="background-color:rgb(255,193,7)">${content}</li></a>`
        }

    } else {
        sidebar_content += "<h3 class='display-1' style='color:rgb(255,193,7)'>Favourite Routes</h3>";
        sidebar_content += "<div class='align-items-center'><ul class='list-group'>"
        let content_arr = content.split(",")
        for (let content of content_arr) {
            sidebar_content += `<a href='javascript:closeSidebar()'><li class="list-group-item fav_routes_button_sb" style="background-color:rgb(255,193,7)">${content}</li></a>`
        }
    }

    sidebar_content += "</ul></div>";
    document.getElementById('sidebar_content').innerHTML = sidebar_content;
    // document.getElementById('sidebar').classList.toggle('active');
    openSidebar()
}

function setupFavButtons(displayStopFromFavs, displayRouteFromFavs) {
    // Function to get all buttons from the sidebar and add an event listener that will call
    // a function which will then call either displayStops or displayRoutes depending on which is needed
    let fav_stops = document.querySelectorAll(".fav_stops_button_sb");
    for (let i = 0; i < fav_stops.length; i++) {
        let current_stop = fav_stops[i];

        current_stop.addEventListener('click', () => {
            displayStopFromFavs(current_stop.innerHTML)
        });
    }
    let fav_routes = document.querySelectorAll(".fav_routes_button_sb");
    for (let i = 0; i < fav_routes.length; i++) {
        let current_route = fav_routes[i];
        current_route.addEventListener('click', () => {
            displayRouteFromFavs(current_route.innerHTML)
        });
    }
}

function openSidebar() {
    document.getElementById("sidebar").style.width = "100%";
}

function closeSidebar() {
    document.getElementById("sidebar").style.width = "0%";

}

function get_timetable_stops(result) {
    var result_1 = JSON.parse(result);
    var stop_list = [];
    var stops = "<span class=\"border border-dark bg-warning border-2\"><div class=\"col-xs-12 col-md-12 text-center fw-bolder\">Stops</div></span>";
    for (let i = 0; i < result_1.length; i++) {
        if (stop_list.includes(result_1[i]["stop"])) {

        } else {
            stop_list.push(result_1[i]["stop"])
        }
    }
    if (stop_list.length == 0) {
        let url = window.location.href
        url = url.replace("%20", " ");
        url = url.replace("%20", " ");
        url = url.replace("%27", "'");
        const myArr = url.split("/");
        document.getElementById('Title').innerHTML = myArr[myArr.length - 1]
        document.getElementById("head_mon_fri").style.display = "none";
        document.getElementById("head_sat").style.display = "none";
        document.getElementById("head_sun").style.display = "none";
        document.getElementById('unavailable').innerHTML = "There doesn't Appear to be any information on this bus Route, Sorry for any inconvenience caused";
        document.getElementById('unavailable').style.display = "visible";
    } else {
        document.getElementById('unavailable').style.display = "none";
        var ordered_stop_list = stop_list.map((i) => Number(i));
        ordered_stop_list.sort((a, b) => a - b);
        for (let i = 0; i < ordered_stop_list.length; i++) {
            if (i == 0) {
                get_timetable(ordered_stop_list[i]);
                stops += "<span class=\"border border-dark bg-warning border-2 active\" onclick=\"get_timetable(" + ordered_stop_list[i] + ")\"><div class=\"col-xs-12 col-md-12 text-center \">" + ordered_stop_list[i] + "</div></span>"
            } else {
                stops += "<span class=\"border border-dark bg-warning border-2\" onclick=\"get_timetable(" + ordered_stop_list[i] + ")\"><div class=\"col-xs-12 col-md-12 text-center \">" + ordered_stop_list[i] + "</div></span>"
            }
        }
        document.getElementById('stop_list').innerHTML = stops;
    }
}

function get_timetable(stop) {
    var stop_time_list = parsedsched
    let url = window.location.href
    url = url.replace("%20", " ");
    url = url.replace("%27", "'");
    const myArr = url.split("/");
    document.getElementById('Title').innerHTML = myArr[myArr.length - 1] + " - Stop " + stop;
    let mon_fri_content = "<div class=\"row\">";
    let sat_content = "<div class=\"row\">";
    let sun_content = "<div class=\"row\">";
    for (let i = 0; i < stop_time_list.length; i++) {
        if ((stop_time_list[i]["day"] == "mon") && (stop_time_list[i]["stop"] == stop)) {
            mon_fri_content += "<div class=\"col-xs-3 col-4 col-2-md col-xl-2 text-center text-warning\">" + stop_time_list[i]["stop_time"] + "</div>"
        } else if ((stop_time_list[i]["day"] == "sat") && (stop_time_list[i]["stop"] == stop)) {
            sat_content += "<div class=\"col-4 col-xs-3 col-2-md col-xl-2 text-center text-warning \">" + stop_time_list[i]["stop_time"] + "</div>"
        } else if ((stop_time_list[i]["day"] == "sun") && (stop_time_list[i]["stop"] == stop)) {
            sun_content += "<div class=\"col-xs-3 col-4 col-2-md col-xl-2 text-center text-warning \">" + stop_time_list[i]["stop_time"] + "</div>"
        }
    }
    mon_fri_content += "</div>"
    sat_content += "</div>"
    sun_content += "</div>"
    document.getElementById('mon_fri_content').innerHTML = mon_fri_content;
    document.getElementById('sat_content').innerHTML = sat_content;
    document.getElementById('sun_content').innerHTML = sun_content;

}

function calculatePrice(stages, fareStatus, leapcard, schoolchild, xpresso) {
    // Function that takes the number of stops passed (stages), fare status and leap card, xpresso and schoolchild booleans
    // as parameters and returns a fare estimation based on this
    let package;
    let cost;
    // First determine package (leap card and fare status combo)
    if (fareStatus === "adult") {
        if (leapcard === true) {
            package = "adultleap";
        } else {
            package = "adultcash";
        }
    } else if (fareStatus === "child") {
        if (leapcard === true) {
            package = "childleap";
        } else {
            package = "childcash";
        }
    }

    //Data structure for costs as per Transport for Ireland website
    let costs = {
        'adultleap': {'price1': 1.55, 'price2': 2.25, 'price3': 2.50, 'price4': 3.00},
        'adultcash': {'price1': 2.15, 'price2': 3.00, 'price3': 3.30, 'price4': 3.80},
        'childleap': {'price1': .80, 'price2': 1.00, 'price3': 1.00, 'price4': 1.26},
        'childcash': {'price1': 1.00, 'price2': 1.30, 'price3': 1.30, 'price4': 1.60}
    };

    if (fareStatus === "adult") {
        if (xpresso === true) {
            cost = costs[package]['price4'];
        } else {
            if (stages >= 1 && stages <= 3) {
                cost = costs[package]['price1'];
            } else if (stages > 3 && stages <= 13) {
                cost = costs[package]['price2'];
            } else if (stages > 13) {
                cost = costs[package]['price3'];
            }
        }
    } else {
        if (schoolchild === true) {
            cost = costs[package]['price1'];
        } else if (xpresso === true) {
            cost = costs[package]['price4'];
        } else {
            if (stages >= 1 && stages <= 7) {
                cost = costs[package]['price2'];
            } else if (stages > 7) {
                cost = costs[package]['price3'];
            }
        }
    }
    return cost;
}
