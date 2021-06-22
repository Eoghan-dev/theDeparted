function scrapeCW() {
    //Function to call the current weather scraper
    fetch('/dublinBus/scrapeCW').then(res => {
        console.log("Scraper request sent")
        if (res.status===200) {
            console.log("Scraper ran succesfully")
        }
        else {
            console.log("scraper failed :(")
        }
    })
}