function scrapeCW() {
    //Function to call the current weather scraper
    fetch('/dublinBus/scrapeCW').then(res => {
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
    fetch('/dublinBus/scrapeCB').then(res => {
        console.log("CurrentBus scraper request sent")
        if (res.status===200) {
            console.log("Scraper ran successfully")
        }
        else {
            console.log("scraper failed :(")
        }
    })
}

function getBusJson() {
    // Funtion to get all bus stops from the current_bus table and return it as json
    fetch('/dublinBus/get_bus_stops').then(res => {
        console.log(res.json())
        return res.json()
    })
}