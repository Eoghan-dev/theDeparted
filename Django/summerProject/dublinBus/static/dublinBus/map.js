async function initMap() {
    // initMap function is ran as soon as our home page is opened
    // Function is async in order to allow use of the await keyword
    // The await keyword is used to make the javascript stop executing until the response is given
    // This is useful for things such as querying our db to get bus stop co-ordinates so that we can ensure that we have
    // these co-ordinates before trying to fill the map with markers based around them.

    // Fill the drop down selector of routes before continuing
    let routes = await fetch('/get_routes').then(res => {
        return res.json()
    }).then(data => {
        console.log("all routes:", data)
        return data
    });

    // load map
    const map = new google.maps.Map(document.getElementById("map"), {
        zoom: 13,
        center: {lat: 53.349804, lng: -6.260310},
    });
    var directionsService = new google.maps.DirectionsService();
    var directionsRenderer = new google.maps.DirectionsRenderer();
    directionsRenderer.setMap(map);

    // Make request to get json object of all dublin bus stops
    // We use await to ensure that we wait until the data is fetched before continuing
    let bus_stop_data = await fetch('/get_bus_stops').then(res => {
        return res.json()
    }).then(data => {
        console.log("bus stop data:", data)
        return data
    });
    // Declare an empty array where we will keep all of our markers for each stop
    const markers_array = [];

    // This is what we can call from our html to load our directions
    const displaySelectedRoute = function () {
        // The first index of the array returned by getElementsByName for our datalist with always be the selected route by the user
        let selectedRoute = document.getElementsByName('routes_num')[0];
        let routeNumber = selectedRoute.value;
        displayRoute(directionsService, directionsRenderer, markers_array, routeNumber)
    };

    // Call the function so the data is loaded in the search bar ready to autocomplete before it's clicked
    loadStopsSearch(bus_stop_data);

    // Add an event listener to a button so we can call the above function which will then load our directions
    document.getElementById("get_directions").addEventListener("click", displaySelectedRoute);

    // Loop through our json object making a marker for each station and placing that marker on the map/saving it to an array
    for (let key in bus_stop_data) {
        let station = bus_stop_data[key];
        // Create info window for each station before creating a marker
        // Save the routes serving this station in a new array by taking the first index from each entry in station.routes
        let station_routes = []
         station.routes.forEach(route => {
            station_routes.push(route[0]);
        })
            // Create content of window
        let window_content = `<h1>Station Name: ${station.stop_name}</h1>` +
            `<ul>` +
                `<li>Station Number: ${station.stop_num} </li>` +
                `<li>Routes served by station: ${station_routes.toString()}` +
            `</ul>`;
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
            number: parseInt(station.stop_num),
            infowindow: current_info_window,
            // Icon taken from http://kml4earth.appspot.com/icons.html
            // icon: "http://maps.google.com/mapfiles/kml/shapes/bus.png", this is the hideous icon
            routes: station.routes,
        });
        // Add an on-click event for each marker to open the associated info window
        current_marker.addListener("click", () => {
            // before opening the window for this marker close any other open markers
            markers_array.forEach(current_marker => {
                current_marker.infowindow.close(map, current_marker)
            });
            current_info_window.open({
                anchor: current_marker,
                map: map,
                shouldFocus: false,
            });
        });
        //Now add each created marker to our array of markers to keep track of them
        markers_array.push(current_marker);
        // Also add each marker to our map
        current_marker.setMap(map);
    }
    console.log("Markers array:", markers_array)
}