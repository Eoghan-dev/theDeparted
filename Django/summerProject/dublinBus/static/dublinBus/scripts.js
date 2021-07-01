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

//  async function getBusJson() {
//     console.log("about to fetch data")
//    let bus_stop_data = await fetch('/dublinBus/get_bus_stops');
//    let bus_stop_json = bus_stop_data.json();
//     return bus_stop_json
// }