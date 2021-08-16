fetch("/timetable_route").then(response => {
    return response.json();
}).then(data => {
    console.log(data)
    results_output = "<div id='resultsTable'>"
    results_output += "<div class='row'><div class='col-xs-6 offset-xs-3 col-8 offset-2 col-md-4 offset-md-4 py-2 my-1 text-center bg-warning'> Station Name </div></div>";
    results_output += "<div class='row'>";
    for (var key in data){
        var arrayLength = data[key]["direction"].length;
        for (var dir = 0; dir < arrayLength; dir++) {
            direction = data[key]["direction"][dir][0]
            var direction_url = direction.replace("'","%27");
            direction_url = direction_url.replace(" ","%20");
            results_output += "<span class=\"border border-dark bg-warning border-5><div class='stname col-md-4 offset-md-4 col-xs-6 offset-xs-3 col-8 offset-2 py-1 my-1 text-center'><a href='/timetable/" + key + ":"+direction_url+"'>" + key + ":"+direction + "</a></div></span>";

            }
    }
    results_output += "</div>";
    document.getElementById("searchresults").innerHTML = results_output;
    results_output += "</div>"
}).catch(err => {
    document.getElementById("searchresults").innerHTML = "<h1>Error! The stations cannot be loaded at this time</h1>";
})
function filterSearch() {
    var input, filter, table, th, a, i, txtValue;
    input = document.getElementById("userInput");
    table = document.getElementById("resultsTable");

    //Search won't be case sensitive.
    filter = input.value.toUpperCase();
    th = table.getElementsByClassName("stname");

    //Anything not matching user query is hidden.
    for (i = 0; i < th.length; i++) {
        a = th[i].getElementsByTagName("a")[0];
        txtValue = a.textContent || a.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            th[i].style.display = "";
        } else {
            th[i].style.display = "none";
        }
    }

}