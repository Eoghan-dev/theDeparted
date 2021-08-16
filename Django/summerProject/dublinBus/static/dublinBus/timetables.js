fetch("/timetable_route").then(response => {
    return response.json();
}).then(data => {
    console.log(data)
    results_output = "<table id='resultsTable'>"
    results_output += "<tr> <th> Station Name </th> <tr>"
    for (var key in data){
        var arrayLength = data[key]["direction"].length;
        for (var dir = 0; dir < arrayLength; dir++) {
            direction = data[key]["direction"][dir][0]
            results_output += "<tr class='stname'>";
            var direction_url = direction.replace("'","%27");
            direction_url = direction_url.replace(" ","%20");
            results_output += "<th class='stname'><a href='/timetable/" + key + ":"+direction_url+"'>" + key + ":"+direction + "</a></th>";
            results_output += "</tr>";
            }
    }


    //Loop through all stations and add a table row for each station.
    //Table ends.
    results_output += "</table>";
    document.getElementById("searchresults").innerHTML = results_output;

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