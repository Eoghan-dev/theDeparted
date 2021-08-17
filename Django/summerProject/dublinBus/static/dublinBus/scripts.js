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

async function displayStop(markersArray, stopNumber, directionsRenderer) {
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
            let current_info_window = marker.infowindow;
            // Make a request to our backend to get the next several buses coming to this stop at time of click
            let incoming_buses_res = await fetch(`get_next_four_bus/${stopNumber}`);
            let incoming_buses = await incoming_buses_res.json();
            console.log(incoming_buses)            // Parse the buses into a string and add this to our info window
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
                      incoming_buses_text += `<li class="list-group-item">${route_name} is currently less than a minute away.</li>`;
                }
                else {
                    incoming_buses_text += `<li class="list-group-item">${route_name} is currently ${minutes_away} minutes away.</li>`;
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
        let currentTimestamp = selectedDateTime.getTime();
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
                        console.log("RESPONSE LOOK HERE:::", response)
                        // Set the directions on the map
                        me.directionsRenderer.setDirections(response);
                        // Get the info we need for our model from the directions response
                        let dir_info = getInfoFromDirections(response, selectedDateTime);
                        let data_for_model = dir_info[0];
                        let trip_info = dir_info[1];
                        let gmaps_total_journey = dir_info[2];
                        // Send the relevant data to our backend so it can get model predictions
                        console.log(data_for_model)
                        let prediction_res = await fetch(`/get_direction_bus/${data_for_model}`);
                        console.log("raw result", prediction_res)
                        let prediction = await prediction_res.json();
                        //console.log("result after .json()", prediction_json)
                        //let prediction = JSON.parse(prediction_json)
                        console.log("result after json.parse", prediction)
                        // Get the html from this data that we want to show to the user and then display it to them
                        let prediction_html = getPredictionHTML(prediction, trip_info, gmaps_total_journey);
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
                                    let trip_info = dir_info[1];
                                    let gmaps_total_journey = dir_info[2];
                                    // Send the relevant data to our backend so it can get model predictions
                                    console.log(data_for_model)
                                    let prediction_res = await fetch(`get_direction_bus/${data_for_model}`);
                                    let prediction_json = await prediction_res.json();
                                    let prediction = JSON.parse(prediction_json)
                                    // Get the html from this data that we want to show to the user and then display it to them
                                    let prediction_html = getPredictionHTML(prediction, trip_info, gmaps_total_journey);
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

function getPredictionHTML(prediction, trip_info, gmaps_total_journey) {
    console.log("trip_info", trip_info)
    let first_walking_time;
    let last_walking_time
    let total_cost = 0.0;
    // first get the number of bus trips that we have in total as we have a prediction for each
    let num_trips = trip_info.length;
    let prediction_html = "<ul class='list-group'>";
    // Use the first for loop to get the indexes (index 0 first step, index 1 second step etc.)
    let gmaps_journey = false; //boolean for whether we're using gmaps predictions or our own
    let transit_count = 0; //counter to differentiate number of transit steps from walking/transit (i)
    for (let i = 0; i < num_trips; i++) {
        prediction_html += "<li class='list-group-item'>";
        // Now loop through the keys from our data returned from backend and get the appropriate
        // index from each of their respective arrays (the value to the key).
        let trip_step = trip_info[i];
        if (trip_step.step_type === "WALKING") {
            prediction_html += trip_step.instructions + " ---- " + trip_step.duration;
            if (i == 0) {
                first_walking_time = parseInt(prediction.departure_time[0]) - parseInt(trip_step.duration.split(" ")[0]) * 1000 * 60
                console.log(new Date(first_walking_time))
            }

        } else {
            let instructions_string_arr = trip_step.instructions.split(" ");
            // remove first element from array and convert back to string
            console.log({prediction})
            instructions_string_arr = instructions_string_arr.slice(1);
            let instructions_string = instructions_string_arr.join(" ");
            prediction_html += "Get route " + trip_step.route_num + " " + instructions_string + " ---- ";
            // if "gmaps" was returned by backend instead of a time we can use the built in google maps prediction
            if (prediction.arrival_time[transit_count] === "gmaps") {
                prediction_html += trip_info[i]["duration"];
                gmaps_journey = true;
            } else {
                // calculate total time taken by step
                let step_time = prediction["arrival_time"][transit_count] - prediction.departure_time[transit_count];
                step_time_date = new Date(step_time)
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
            console.log("num stops is " + stops_passed + " and fare status is " + fare_status + " and leap card is " + leap_card)

            // calculate cost of bus by first calculating whether the current departure time falls within a schooltime range
            let departure_time = trip_info[i].departure_time;
            let schooltime = determineSchoolRange(departure_time);
            // check if route is xpresso (has an x in the route number)
            console.log({trip_step})
            let xpresso = (trip_step.route_num.includes("x") || trip_step.route_num.includes("X"));
            let fare = calculatePrice(stops_passed, fare_status, leap_card, schooltime, xpresso);
            prediction_html += " ---- €" + fare.toFixed(2);
            total_cost += fare;
            transit_count += 1;
        }
        prediction_html += "</li>";
    }
    if (trip_info[trip_info.length - 1].step_type === "WALKING") {
        last_walking_time = parseInt(prediction["arrival_time"][prediction["arrival_time"].length - 1]) + parseInt(trip_info[trip_info.length - 1].duration.split(" ")[0]) * 1000 * 60
    }
    prediction_html += "</ul>";
    // Get total time of journey
    let total_time_taken_str = "";
    if (gmaps_journey) {
        total_time_taken_str = "Total journey should take " + gmaps_total_journey + "and should cost €" + total_cost.toFixed(2);
    } else {
        console.log("prediction.arrival_time[num_trips - 1]", prediction.arrival_time[num_trips - 1])
        console.log(prediction["departure_time"][0])
        let time_taken_timestamp = Math.abs(prediction.arrival_time[num_trips - 1] - prediction.departure_time[0]);
        console.log("time_taken_timestamp", time_taken_timestamp)
        let hours_taken = (time_taken_timestamp / 1000) / 3600;
        let minutes_taken = (time_taken_timestamp / 1000) / 60;
        total_time_taken_str = "Total journey should take " + ((last_walking_time - first_walking_time) / 1000 / 60) + " minutes and should cost €" + total_cost.toFixed(2);
    }

    prediction_html += total_time_taken_str;
    return prediction_html
}
function determineSchoolRange(departure_time) {
    let valid = false;
    let departure_min;
    // Function to determine if a bus departure time falls within a school range for our fare calculator
    console.log("departure time", departure_time)
    let departure_hour = parseInt(departure_time.split(":")[0]);
    // Parse the departure time minutes differently depending on if response includes pm/am
    if (departure_time.split(":")[1].includes("pm") || departure_time.split(":")[1].includes("am")) {
        departure_min = parseInt(departure_time.split(":")[1].substring(0, 2));
        if (departure_time.split(":")[1].substring(2,4) === "pm") {
            departure_hour += 12;
        }
    }
    else {
        departure_min = parseInt(departure_time.split(":")[1])
    }

    let date = new Date();
    // set the departure time to our date object
    console.log(departure_min)
    date.setHours(departure_hour);
    date.setMinutes(departure_min);
    // get the day of the week (sunday is 0)
    let weekday = date.getDay();
    // valid until 19:00 mon-fri and until 13:30 on saturday. Never valid on sunday
    if (weekday === 7) {
        // If it's before 1pm or after 1pm but before 1.30pm then it's valid
        if ((date.getHours() < 13 ) || (date.getHours() < 14 && date.getHours() >= 13 && date.getMinutes() < 30)) {
            valid = true;
        }
    }
    else if (weekday === 0) {
        // Do nothing if it's sunday since it's never valid
    }
    else {
        // For mon-fri it's valid if it's before 19:00
        if (date.getHours() < 19) {
            console.log(date.getHours(), "is less than 19, valid")
            valid = true;
        }
    }
    return valid;
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
    console.log({now})
    let current_date = now.toISOString().split("T")[0]; // https://stackoverflow.com/a/49916376
    date_input.setAttribute("min", current_date);
    date_input.setAttribute("value", current_date);
    // create new date object as five days later and set as max
    let max_date = now;
    let current_day = now.getDate();
    let future_day = current_day + 5;

    max_date.setDate(future_day)
    console.log({max_date})
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
            console.log("GMAPS TOTAL JOURNEY TIME:", current_leg.duration.text)
            gmaps_total_journey_time = current_leg.duration.text;
            console.group("current_leg is:", current_leg)
            // Loop through each step in this leg of the route
            for (let k = 0; k < current_leg.steps.length; k++) {
                let current_step = current_leg.steps[k];
                console.group("current_step is:", current_step)
                // Check if this step is using public transport and if so check if it's using the correct route
                let step_info = {}
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

                    step_info["step_type"] = current_step.travel_mode;
                    step_info["distance"] = current_step.distance;
                    step_info["instructions"] = current_step.instructions;
                    step_info["duration"] = current_step.duration.text;
                    step_info["gmaps_prediction"] = current_step.transit.arrival_time.value;
                    step_info["departure_time"] = departure_time;
                    step_info["route_num"] = current_step.transit.line.short_name;
                    step_info["num_stops"] = current_step.transit.num_stops;
                } else {
                    console.log("step is not transit")
                    // save step info with no detail for gmaps prediction as this is only needed for bus times
                    step_info["step_type"] = current_step.travel_mode;
                    step_info["distance"] = current_step.distance;
                    step_info["instructions"] = current_step.instructions;
                    step_info["duration"] = current_step.duration.text;
                    step_info["gmaps_prediction"] = "n/a";
                    if (k === 0) {
                        step_info["departure_time"] = current_leg.departure_time;
                    }
                    else {
                        step_info["departure_time"] = "n/a";
                    }
                    step_info["route_num"] = "n/a";
                    step_info["num_stops"] = "n/a";
                }
                trip_description.push(step_info);
            }
        }
    }
    console.log(data_for_model);
    // Return our objects
    let data_for_model_json = JSON.stringify(data_for_model);
    return [data_for_model_json, trip_description, gmaps_total_journey_time];
}

function fillSidebar(content, type) {
    // takes a parameter of user's fav routes/stops
    console.log("in fill sidebar")
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
    console.log("inside setup fav buttons")
    let fav_stops = document.querySelectorAll(".fav_stops_button_sb");
    console.log({fav_stops_buttons: fav_stops})
    for (let i=0; i< fav_stops.length; i++) {
        let current_stop = fav_stops[i];

        current_stop.addEventListener('click', () => {
            console.log("in sidebar button event listener (stop)")
            displayStopFromFavs(current_stop.innerHTML)
        });
    }
    let fav_routes = document.querySelectorAll(".fav_routes_button_sb");
    console.log({fav_routes_buttons: fav_routes})
    for (let i=0; i< fav_routes.length; i++) {
        let current_route = fav_routes[i];
          current_route.addEventListener('click', () => {
              console.log("in sidebar button event listener (route)")
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
    console.log("back again")
    var stops = "<span class=\"border border-dark bg-warning border-2\"><div class=\"col-xs-12 col-md-12 text-center fw-bolder\">Stops</div></span>";
    for (let i = 0; i < result_1.length; i++) {
        if (stop_list.includes(result_1[i]["stop"]))   {

        }
        else    {

            //stops += "<span class=\"border border-dark bg-warning border-2\"><div class=\"col-xs-12 col-md-12 text-center \">"+result_1[i]["stop"]+"</div></span>"
            //var stop = result_1[i]["stop"];
            //var entry = document.createElement('li');
            //entry.hre
            //entry.classList.add("list-group-item");
            //entry.appendChild(document.createTextNode(stop));
            //list.appendChild(entry);
            stop_list.push(result_1[i]["stop"])
        }
    }
    var ordered_stop_list = stop_list.map((i) => Number(i));
    ordered_stop_list.sort((a, b) => a - b);
    for (let i = 0; i < ordered_stop_list.length; i++) {
        console.log("back again")
        stops += "<span class=\"border border-dark bg-warning border-2\" onclick=\"get_timetable("+ ordered_stop_list[i] +")\"><div class=\"col-xs-12 col-md-12 text-center \">"+ordered_stop_list[i]+"</div></span>"
    }
    document.getElementById('stop_list').innerHTML = stops;
}
function get_timetable(stop) {
    var stop_time_list = parsedsched
    console.log(stop)
    let url = window.location.href
    url = url.replace("%20", " ");
    url = url.replace("%27", "'");
    const myArr = url.split("/");
    document.getElementById('Title').innerHTML = myArr[myArr.length - 1] + " - Stop " + stop;
    let mon_fri_content = "<div class=\"row\">";
    let sat_content = "<div class=\"row\">";
    let sun_content = "<div class=\"row\">";
    for (let i = 0; i < stop_time_list.length; i++) {
        if ((stop_time_list[i]["day"]=="mon")&&(stop_time_list[i]["stop"]==stop)   ) {
            mon_fri_content += "<div class=\"col-xs-3 col-4 col-2-md col-xl-2 text-center text-warning\">"+ stop_time_list[i]["stop_time"] +"</div>"
        }
        else if ((stop_time_list[i]["day"]=="sat")&&(stop_time_list[i]["stop"]==stop))    {
            sat_content += "<div class=\"col-4 col-xs-3 col-2-md col-xl-2 text-center text-warning \">"+ stop_time_list[i]["stop_time"] +"</div>"
        }
        else if ((stop_time_list[i]["day"]=="sun" )&&(stop_time_list[i]["stop"]==stop))    {
            sun_content += "<div class=\"col-xs-3 col-4 col-2-md col-xl-2 text-center text-warning \">"+ stop_time_list[i]["stop_time"] +"</div>"
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
    console.log("fare status of user is", fareStatus)
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
    var costs = {
        'adultleap': {'price1': 1.55, 'price2' : 2.25, 'price3': 2.50, 'price4': 3.00},
        'adultcash': {'price1': 2.15, 'price2' : 3.00, 'price3': 3.30, 'price4': 3.80},
        'childleap': {'price1': .80, 'price2' : 1.00, 'price3': 1.00, 'price4': 1.26},
        'childcash': {'price1': 1.00, 'price2' : 1.30, 'price3': 1.30, 'price4': 1.60}
    };

    if (fareStatus === "adult") {
        if (xpresso === true) {
            cost = costs[package]['price4'];
            console.log("found fare, cost is", cost, "and package is", package)
        }
        else {
            if (stages >= 1 && stages <= 3) {
                cost = costs[package]['price1'];
                console.log("found fare, cost is", cost, "and package is", package)
            } else if (stages > 3 && stages <= 13) {
                cost = costs[package]['price2'];
                console.log("found fare, cost is", cost, "and package is", package)
            } else if (stages > 13) {
                cost = costs[package]['price3'];
                console.log("found fare, cost is", cost, "and package is", package)
            }
        }
    }
    else {
        if (schoolchild === true) {
            cost = costs[package]['price1'];
            console.log("found fare, cost is", cost, "and package is", package)
        } else if (xpresso === true) {
            cost = costs[package]['price4'];
            console.log("found fare, cost is", cost, "and package is", package)
        }
        else {
            if (stages >= 1 && stages <= 7) {
                cost = costs[package]['price2'];
                console.log("found fare, cost is", cost, "and package is", package)
            } else if (stages > 7) {
                cost = costs[package]['price3'];
                console.log("found fare, cost is", cost, "and package is", package)
            }
        }
    }




    //if else statements to return price based on dropdown selection
  //   if(stages == 1 && package =='adultleap') {
  //       console.log('stage', stages);
  //       console.log(costs['adultleap'].price1);
  //       var price = costs['adultleap'].price1;
  //   }
  //   else if(stages == 1 && package =='adultcash') {
  //       console.log('stage', stages);
  //       console.log(costs['adultcash'].price1);
  //       var price = costs['adultcash'].price1;
  //   }
  //   else if(stages == 2 && package =='adultleap') {
  //       console.log('stage', stages);
  //       console.log(costs['adultleap'].price2);
  //       var price = costs['adultleap'].price2;
  //   }
  //   else if(stages == 2 && package =='adultcash') {
  //       console.log('stage', stages);
  //       console.log(costs['adultcash'].price2);
  //       var price = costs['adultcash'].price2;
  //   }
  //   else if(stages == 3 && package =='adultleap') {
  //       console.log('stage', stages);
  //       console.log(costs['adultleap'].price3);
  //       var price = costs['adultleap'].price3;
  //   }
  //   else if(stages == 3 && package =='adultcash') {
  //       console.log('stage', stages);
  //       console.log(costs['adultcash'].price3);
  //       var price = costs['adultcash'].price3;
  //   }
  //   else if(stages == 4 && package =='adultleap') {
  //       console.log('stage', stages);
  //       console.log(costs['adultleap'].price4);
  //       var price = costs['adultleap'].price4;
  //   }
  //   else if(stages == 4 && package =='adultcash') {
  //       console.log('stage', stages);
  //       console.log(costs['adultcash'].price4);
  //       var price = costs['adultcash'].price4;
  //   }
  //   else if(stages == 5 && package =='childleap') {
  //       console.log('stage', stages);
  //       console.log(costs['childleap'].price1);
  //       var price = costs['childleap'].price1;
  //   }
  //   else if(stages == 5 && package =='childcash') {
  //       console.log('stage', stages);
  //       console.log(costs['childcash'].price1);
  //       var price = costs['childcash'].price1;
  //   }
  //   else if(stages == 6 && package =='childleap') {
  //       console.log('stage', stages);
  //       console.log(costs['childleap'].price2);
  //       var price = costs['childleap'].price2;
  //   }
  //   else if(stages == 6 && package =='childcash') {
  //       console.log('stage', stages);
  //       console.log(costs['childcash'].price2);
  //       var price = costs['childcash'].price2;
  //   }
  //   else if(stages == 7 && package =='childleap') {
  //       console.log('stage', stages);
  //       console.log(costs['childleap'].price3);
  //       var price = costs['childleap'].price3;
  //   }
  //   else if(stages == 7 && package =='childcash') {
  //       console.log('stage', stages);
  //       console.log(costs['childcash'].price3);
  //       var price = costs['childleap'].price3;
  //   }
  //   else if(stages == 8 && package =='childleap') {
  //       console.log('stage', stages);
  //       console.log(costs['childleap'].price4);
  //       var price = costs['childleap'].price4;
  //   }
  //   else if(stages == 8 && package =='childcash') {
  //       console.log('stage', stages);
  //       console.log(costs['childcash'].price4);
  //       var price = costs['childleap'].price4;
  //   }
  //   else {
  //     var price = 'Invalid Selction';
  //   }
  //
  // document.getElementById('price').innerHTML = price;
        return cost;
}
