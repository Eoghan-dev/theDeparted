

async function initMap() {
  // initMap function is ran as soon as our home page is opened
  // Function is async in order to allow use of the await keyword
  // The await keyword is used to make the javascript stop executing until the response is given
  // This is useful for things such as querying our db to get bus stop co-ordinates so that we can ensure that we have
  // these co-ordinates before trying to fill the map with markers based around them.

  // load map
  const map = new google.maps.Map(document.getElementById("map"), {
    zoom: 4,
    center: {lat: 53.349804, lng: -6.260310},
  });
  // Make request to get json object of all dublin bus stops
  // We use await to ensure that we wait until the data is fetched before continuing
  let bus_stop_data = await fetch('/dublinBus/get_bus_stops').then(res=> {
    return res.json()
  }).then(data => {
    console.log(data)
    return data
  })
  console.log("look here")
  console.log(typeof bus_stop_data)
  console.log(bus_stop_data)

  // Declare an empty array where we will keep all of our markers for each stop
  let markers_array = [];
  // Apply this arrow function to each bus station in our response
  bus_stop_data.forEach(station=> {
    let station_long = parseFloat(station.stop_lon);
    let station_lat = parseFloat(station.stop_lat);
    const marker = new google.maps.Marker({
      position: {lat: station_lat, long: station_long},
      map: map,
      name: station.name,
      number: parseInt(station.number),
    });

    if (station.stop_id === 1) {
      console.log(station.name)
    }
    //Now add each created marker to our array of markers to keep track of them
    markers_array.push(marker);
    // Also add each marker to our map
    marker.setMap(map)
  });
}