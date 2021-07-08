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

function showCertainMarkers(allMarkers, visibleMarkers, map) {
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