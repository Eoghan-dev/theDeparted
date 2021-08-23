async function initMap() {
    // initMap function is ran as soon as our home page is opened
    // Function is async in order to allow use of the await keyword
    // The await keyword is used to make the javascript stop executing until the response is given
    // This is useful for things such as querying our db to get bus stop co-ordinates so that we can ensure that we have
    // these co-ordinates before trying to fill the map with markers based around them.
    // Make requests to get json object of all routes

    // Load necessary event listeners and values into our directions input from user (date/time etc)
    loadDirUserInput();
    let routes = await loadRoutes();

    // load map
    const map = new google.maps.Map(document.getElementById("map"), {
        zoom: 13,
        center: {lat: 53.349804, lng: -6.260310},
        mapTypeControl: false,
    });
    var directionsService = new google.maps.DirectionsService();
    var directionsRenderer = new google.maps.DirectionsRenderer();
    directionsRenderer.setMap(map);

    // Make request to get json object of all dublin bus stops
    // We use await to ensure that we wait until the data is fetched before continuing
    let bus_stop_data = await loadStops();

    // Declare an empty array where we will keep all of our markers for each stop
    const markers_array = [];

    // This is what we can call from our html to load our directions
    const displaySelectedRoute = function () {
        // The first index of the array returned by getElementsByName for our datalist with always be the selected route by the user
        let selectedRoute = document.getElementsByName('routes_num')[0];
        let routeNumberAndDir = selectedRoute.value;
        displayRoute(directionsService, directionsRenderer, markers_array, routeNumberAndDir)
    };
    const displaySelectedStop = function () {
        // The first index of the array returned by getElementsByName for our datalist with always be the selected stop by the user
        let selectedStop = document.getElementsByName('stops_num')[0];
        let stopNum = selectedStop.value;
        displayStop(markers_array, stopNum, directionsRenderer)
    };
    loadDataListsHome(bus_stop_data, routes, displaySelectedRoute, displaySelectedStop);

    const displayStopFromFavs = function(stopNum) {
        displayStop(markers_array, stopNum, directionsRenderer);
    }
    const displayRouteFromFavs = function(route) {
        displayRoute(directionsService, directionsRenderer, markers_array, route);
    }

    // Every time either the fav routes or fav stops button is clicked run this function to add event listeners to all the buttons
    // Only do this if the user is logged in and the buttons are present
    if (document.getElementById('fav_stops_btn')) {
        document.getElementById('fav_stops_btn').addEventListener('click', () => {
            setupFavButtons(displayStopFromFavs, displayRouteFromFavs)
        });
        document.getElementById('fav_routes_btn').addEventListener('click', () => {
            setupFavButtons(displayStopFromFavs, displayRouteFromFavs)
        })
    }


    // Loop through our json object making a marker for each station and placing that marker on the map/saving it to an array
    for (let key in bus_stop_data) {
        let station = bus_stop_data[key];
        // Create info window for each station before creating a marker
        // Save the routes serving this station in a new array by taking the first index from each entry in station.routes
        let station_routes = []
        let station_number = key; //

        station.routes.forEach(route => {
            // Make a combined string of the first index of each entry in routes (route number) and the second (direction of route)
            let routes_string = route[0] + ": " + route[1];
            station_routes.push(routes_string);
        })
        // Create content of window
        let window_content = `<div class="infowindow"><h2> Stop ${station_number}: ${station.stop_name}</h2>` +
            `Routes serving this station:`;
        window_content +="<br><a>";
        for (let route of station_routes) {
            window_content += `${route}<br>`;
        }
        window_content +="</a>";
        // Create info window object
        let current_info_window = new google.maps.InfoWindow({
            content: window_content,
        });

        // Create marker for each station
        const current_marker_location = new google.maps.LatLng(station.stop_lat, station.stop_lon);
        const current_marker = new google.maps.Marker({
            position: current_marker_location,
            map: map,
            name: station.stop_name,
            number: station_number,
            infowindow: current_info_window,
            //label: station_number,
            // Icon taken from http://kml4earth.appspot.com/icons.html
            // icon: "http://maps.google.com/mapfiles/kml/shapes/bus.png", this is the hideous icon
            routes: station_routes,
        });
        // Add an on-click event for each marker to open the associated info window
        current_marker.addListener("click", async () => {
            // document.getElementById('map').classList.toggle("spinner-border")
            // before opening the window for this marker close any other open markers
            markers_array.forEach(current_marker => {
                current_marker.infowindow.close(map, current_marker)
            });
            // Make a request to our backend to get the next several buses coming to this stop at time of click
            let incoming_buses_res = await fetch(`/get_next_four_bus/${current_marker.number}`);
            let incoming_buses = await incoming_buses_res.json();
            // Parse the buses into a string and add this to our info window
            // Get the static part of the info window before overwriting it
            let previous_info_window_text = current_info_window.getContent();
            let previous_content = previous_info_window_text.split("<h3>")[0];
            let info_window_text = previous_content;

            let incoming_buses_text = "<h3>Incoming Buses</h3>" +
                "<ul class='list-group'>";
            // Loop over the incoming bus data and each of them to the info window
            for (let route of incoming_buses) {
                let route_name = route[0];
                let minutes_away = route[1];
                if (minutes_away == 0) {
                    incoming_buses_text += `<li class="list-group-item">${route_name} is less than a minute away.</li>`;
                }
                else {
                    incoming_buses_text += `<li class="list-group-item">${route_name} ${minutes_away} minutes away.</li>`;
                }
            }
            incoming_buses_text += "</ul></div>";
            info_window_text += incoming_buses_text;
            current_info_window.setContent(info_window_text);
            current_info_window.open({
                anchor: current_marker,
                map: map,
                shouldFocus: true,
            });
        });
        //Now add each created marker to our array of markers to keep track of them
        markers_array.push(current_marker);
        // Also add each marker to our map
        current_marker.setVisible(false)
        current_marker.setMap(map);
    }
    // We can initialise our class to handle directions here once we've declared all the arguments and filled the markers array
    new AutocompleteDirectionsHandler(map, markers_array, directionsService, directionsRenderer);

    // Get user geolocation (adapted from https://developers.google.com/maps/documentation/javascript/examples/map-geolocation)
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const pos = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude,
                };
                const user_marker = new google.maps.Marker({
                    position: pos,
                    map: map,
                    name: "user location",
                    // Icon taken from http://kml4earth.appspot.com/icons.html
                    icon: "http://maps.google.com/mapfiles/kml/shapes/man.png",
                });
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

