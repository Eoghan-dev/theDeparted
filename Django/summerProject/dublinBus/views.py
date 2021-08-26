from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from .models import CurrentWeather, CurrentBus, BusStops, WeatherForecast, Current_timetable_all
from django.conf import settings # This allows us to import base directory which we can use for read/write operations
import os
import pandas as pd
import pickle
import datetime
from dateutil.relativedelta import *
from datetime import timedelta, datetime
base = settings.BASE_DIR
from urllib.request import urlopen
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
import json
import math
import gzip
import time

def index(request):
    """View to load the homepage of our application
    Also loads all cancelled routes and times for display
    under routes tab
    """
    #Gets current time and changes it to the desired format HH:MM:SS
    start_time = time.time()
    with urlopen("https://www.timeapi.io/api/Time/current/zone?timeZone=Europe/Dublin") as url:
        s = url.read()
        dub_t =json.loads(s)
    print(dub_t["dateTime"])
    dub_date_time = dub_t["dateTime"][:-1]
    dub_date_time = datetime.strptime(dub_date_time.replace("T", " "), '%Y-%m-%d %H:%M:%S.%f')
    print("--- %s seconds ---" % (time.time() - start_time))
    cur_time = str(dub_date_time.time())
    cur_time_list = list(cur_time.split(":"))
    cur_time = cur_time_list[0] + ":" + cur_time_list[1] + ":00"
    result = CurrentBus.objects.filter(schedule="CANCELED", start_t__gt=cur_time).values()
    #Gets weekdays and converts to an integer to match mon/sat/sun in json files
    weekday = int(dub_date_time.weekday())
    list_return = []
    if weekday < 5:
        day = "mon"
    elif weekday == 5:
        day = "sat"
    elif weekday == 6:
        day = "sun"
    for i in result:
        #intialise lists and dictionaries that will be refreshed for each result
        dict_return = {}
        headsigns_li = []
        route = i["route"]
        start_t = i["start_t"]
        direction = i["direction"]
        #Opens routes.json file
        file_path_routes = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files",
                                       "routes.json")
        f = open(file_path_routes, encoding="utf-8-sig")
        routes_dict = json.load(f)
        f.close()
        #Matches the directions/headsigns to that outputted from the database
        for dir in routes_dict[route]["direction"]:
            if dir[1] == direction:
                headsigns_li.append(dir[0])
        #If only one route for that direction must be this direction that is refrenced
        if len(headsigns_li) == 1:
            dict_return["route"] = route
            dict_return["headsign"] = headsigns_li[0]
            dict_return["time"] = start_t
        #Else we must check the timtable to tell which headsign is correct
        else:
            file_path_times = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files","bus_times", route + "_timetable.json")
            if os.path.isfile(file_path_times) == True:
                f = open(file_path_times, encoding="utf-8-sig")
                times_dict = json.load(f)
                f.close()
                success = 0
                #Iterates through the timetable until it finds a matching route
                for headsign in headsigns_li:
                    if headsign in times_dict:
                        if day in times_dict[headsign]:
                            for stop in times_dict[headsign][day]:
                                for times in times_dict[headsign][day][stop]:
                                    #if start time from database is matched with the static json success and saves to returned dictionary
                                    if times[0] == start_t:
                                        dict_return["route"] = route
                                        dict_return["headsign"] = headsign
                                        dict_return["time"] = start_t
                                        break
        list_return.append(dict_return)
    return render(request, 'dublinBus/index.html', {"result": list_return})

def dbTwitter(request):
    """View to load the Dublin bus twitter feed to our application"""
    return render(request, 'dublinBus/twitter.html')

def aboutUs(request):
    """View to load the about us page to our application"""
    return render(request, 'dublinBus/aboutUs.html')

def myAccount(request):
    """View to load the accounts page of our application"""
    # If request was posted then a change was made to the password reset form on the page
    if request.method == 'POST':
        # Ensure that it was the password change form that was clicked and not any of the other post requests
        # if 'password_change' in request.POST:
        print("found")
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('myAccount')
    else:
        form = PasswordChangeForm(request.user)

    # Regardless of the form loaded above we also want to parse the users stops and routes into arrays and pass them
    # to the page in that form instead of as a comma seperated string
    # initialise fav routes and stops json before the if statement so that they can be passed to page even if empty
    fav_stops_list = []
    fav_routes_list = []
    timetable_li = []
    if request.user.is_authenticated:
        user = request.user
        # Get users fav routes and stops, convert to array and then convert to json so it can be passed as a context
        fav_routes = user.favourite_routes.strip()
        fav_routes_list = fav_routes.split(",")
        # Check if the first index is empty and remove it if so (bug with unknown cause)
        if len(fav_routes_list[0]) < 1:
            del fav_routes_list[0]
        fav_routes_json = json.dumps(fav_routes_list)
        fav_stops = user.favourite_stops.strip()
        fav_stops_list = fav_stops.split(",")
        # Check if the first index is empty and remove it if so (bug with unknown cause)
        if len(fav_stops_list[0]) < 1:
            del fav_stops_list[0]
        print(fav_routes)
        print("LOOK HERE", fav_stops_list)
        fav_stops_json = json.dumps(fav_stops_list)
    return render(request, 'dublinBus/myAccount.html', {'form': form, 'fav_routes': fav_routes_list, 'fav_stops': fav_stops_list})

def updateUser(request):
    """View to update user fare status and leap card from user settings page"""
    if request.method == "POST":
        # Get the values for fare_status and leap card
        fare_status = request.POST.get('fare_status_radios')
        leap_card_str = request.POST.get('leap_card_radios')
        # Parse the leap card string returned to get boolean
        print("leap card str", leap_card_str)
        if leap_card_str == "true":
            leap_card = True
        else:
            leap_card = False
        # Get the instance of our user model being used
        user = request.user
        # Make changes and save to db
        user.fare_status = fare_status
        user.leap_card = leap_card
        user.save()
        return redirect('myAccount')
    else:
        return HttpResponse("error with updating user settings")

def addUserRoute(request):
    """View to update users favourite routes from favourites tab in my account page"""
    # Get the route that was selected by the user
    user_route = request.POST.get('user_routes_form')
    print(user_route)
    # Manually validate that this is one of the routes in routes.json
    # Save the path of shapes.json as a variable
    file_path = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files", "routes.json")
    # Open the file and load it as a dictionary
    f = open(file_path, encoding="utf-8-sig")
    routes_dict = json.load(f)
    # Get all values from the dictionary so we have a list of dictionaries with the data we want
    routes = routes_dict.values()
    # remove any dictionaries from the list with the duplicate route short names, effectively halving the list
    # Make a set with all the route numbers(route_short_name) so there's no duplicates
    found_routes = set()
    halved_routes = []
    for route in routes:
        if route['route_short_name'] not in found_routes:
            halved_routes.append(route)
            # Before adding the current route dict to the set we need to cast it to a tuple as you can't add dicts to sets
            found_routes.add(route['route_short_name'])
    # Now look through the halved array to check that the route + headsign that was entered by the user actually exists
    for route in halved_routes:
        if route['direction']:
            for direction in route['direction']:
                route_and_headsign = route['route_short_name'] + ": " + direction[0]
                print(route_and_headsign)
                # If the route + headsign was valid (exists in our dict) then save it to the users profile
                if route_and_headsign == user_route:
                    user = request.user
                    previous_fav_routes = user.favourite_routes
                    # Convert from comma seperated string to a list
                    fav_routes_list = previous_fav_routes.split(",")
                    # Check if the route the user selected is already added to favourites and return early if so
                    if user_route in fav_routes_list:
                        return redirect('myAccount')
                    else:
                        fav_routes_list.append(user_route)
                        # Remove empty item from start of list
                        if len(fav_routes_list[0]) < 1:
                            del fav_routes_list[0]
                        # Convert back from list to comma seperated string
                        new_fav_routes = ",".join(fav_routes_list)
                        user.favourite_routes = new_fav_routes.strip()
                        user.save()
                        return redirect('myAccount')
    # If the route entered by the user wasn't found return an error
    return redirect('myAccount')

def addUserStop(request):
    """View to update users favourite stops from favourites tab in my account page"""
    # Get the route that was selected by the user
    user_stop = request.POST.get('user_stops_form')
    # Manually validate that this is one of the routes in routes.json
    # Save the path of shapes.json as a variable
    file_path = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files", "stops.json")
    # Open the file and load it as a dictionary
    f = open(file_path, encoding="utf-8-sig")
    stops_dict = json.load(f)
    # Get all values from the dictionary so we have a list of dictionaries with the data we want
    stops = stops_dict.keys()

    # Look through our list of stop dictionaries and check if the stop number entered by the user exists
    for stop in stops:
        if stop == user_stop:
            # If the stop number exists we can save it
            user = request.user
            previous_fav_stops = user.favourite_stops
            # Convert from comma seperated string to a list
            fav_stops_list = previous_fav_stops.split(",")
            # Check if the stop the user selected is already added to favourites and return early if so
            if user_stop in fav_stops_list:
                return redirect('myAccount')
            fav_stops_list.append(user_stop)
            if len(fav_stops_list[0]) < 1:
                del fav_stops_list[0]
            # Convert back from list to comma seperated string
            new_fav_stops = ",".join(fav_stops_list)
            user.favourite_stops = new_fav_stops
            user.save()
            return redirect('myAccount')
    # If the route entered by the user wasn't found return an error
    return redirect('myAccount')

def delUserRoute(request, route):
    """View to delete a particular route chosen by the user"""
    user = request.user
    fav_routes = user.favourite_routes
    # Convert to array and remove the passed route from it
    fav_routes_list = fav_routes.split(",")
    fav_routes_list.remove(route)
    # Convert back to comma seperated string
    fav_routes = ",".join(fav_routes_list)
    user.favourite_routes = fav_routes
    user.save()
    return redirect('myAccount')

def delUserStop(request, stop):
    """View to delete a particular stop chosen by the user"""
    user = request.user
    fav_stops = user.favourite_stops
    # Convert to array and remove the passed route from it
    fav_stops_list = fav_stops.split(",")
    fav_stops_list.remove(stop)
    # Convert back to comma seperated string
    fav_stops = ",".join(fav_stops_list)
    user.favourite_stops = fav_stops
    user.save()
    return redirect('myAccount')

def get_next_bus_time(request, route):
    """View to return the closest scheduled departure time for a certain bus route to the current time"""
    with urlopen("https://www.timeapi.io/api/Time/current/zone?timeZone=Europe/Dublin") as url:
        s = url.read()
        dub_t =json.loads(s)
    print(dub_t["dateTime"])
    dub_date_time = dub_t["dateTime"][:-1]
    dub_date_time = datetime.strptime(dub_date_time.replace("T", " "), '%Y-%m-%d %H:%M:%S.%f')
    current_date_time = dub_date_time
    current_24hr_time = current_date_time.strftime("%H:%M:%S")
    # Open the json file of all route timetables as a dictionary
    file_path = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files", "bus_times.json")
    # Open the file and load it as a dictionary
    f = open(file_path, encoding="utf-8-sig")
    timetable_dict = json.load(f)
    # parse the route number and headsign seperately from route
    route_arr = route.split(":")
    route_num = route_arr[0]
    route_headsign = route_arr[1].strip()
    # find the route number from the timetable
    route_num_timetable = timetable_dict[route_num]
    # Find the correct headsign from within this route
    route_timetable = route_num_timetable[route_headsign]
    # Get the correct timetable based on the current day (can be sat/sun/mon-fri)
    # Get current day of the week (0=monday and 6=sunday)
    current_day = datetime.today().weekday()
    if current_day == 5:
        times = list(route_timetable['sat'].values())[0]
        # Get the stop number for the start of this route + headsign
        start_stop_num = list(route_timetable['sat'].keys())[0]
        # Save the start stop number for the route to a variable as we will return it later
    elif current_day == 6:
        times = list(route_timetable['sun'].values())[0]
        # Get the stop number for the start of this route + headsign
        start_stop_num = list(route_timetable['sun'].keys())[0]
    else:
        times = list(route_timetable['mon'].values())[0]
        # Get the stop number for the start of this route + headsign
        start_stop_num = list(route_timetable['mon'].keys())[0]

    # start_stop_num = list(route_timetable.keys())[0]
    # get the end stop number for this route
    # Load stops.json as a dictionary
    file_path = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files", "stops.json")
    f = open(file_path, encoding="utf-8-sig")
    stops_dict = json.load(f)
    # look up the start stop in this
    start_stop_data = stops_dict[start_stop_num]
    start_stop_coords = {'lat': start_stop_data['stop_lat'], 'lon': start_stop_data['stop_lon']}
    # Get the end stop number
    start_stop_routes = start_stop_data['routes']
    for stop_route in start_stop_routes:
        print(stop_route)
        print(route_num, route_headsign, start_stop_num)
        if stop_route[0] == route_num and stop_route[1] == route_headsign and int(stop_route[4]) == int(start_stop_num):
            end_route_num = stop_route[5]
    # Get the coordinates for the end stop
    end_stop_data = stops_dict[end_route_num]
    end_stop_coords = {'lat': end_stop_data['stop_lat'], 'lon': end_stop_data['stop_lon']}
    route_start_and_end = [start_stop_coords, end_stop_coords]

    # Make an array with all the times converted to a datetime object (hours and minutes only)
    converted_times = list(map(lambda x: datetime.strptime(x, "%H:%M:%S"), times))
    # Get current time as datetime object also with only hours and minutes
    now = dub_date_time.strftime("%H:%M:%S")
    now_dt = datetime.strptime(now, "%H:%M:%S")
    # Remove all items from the timetable list that are before the current time as they're useless in this context
    filtered_times = list(filter(lambda x: x >= now_dt, converted_times))
    # Check if any times existed or if it's too late in the day
    if len(filtered_times) > 0:
        # Now find the closest match in filtered time to the current time
        closest_time = min(filtered_times, key=lambda dt: abs(dt - now_dt))
        # Extract the hour and minutes as a string and return it
        closest_time_str = closest_time.strftime("%H:%M:%S")
        returnable_data = {'time': closest_time_str, 'coords': route_start_and_end}
        return JsonResponse(returnable_data)
    else:
        return HttpResponse("error")

def get_bus_stops(request):
    """View to get all bus stops from our json file and return it as a json object"""
    file_path = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files", "stops.json")
    bus_stops_json = list(BusStops.objects.values())
    f = open(file_path, encoding="utf-8-sig")
    stops_dict = json.load(f)
    return JsonResponse(stops_dict)

def get_routes(request):
    """View to get all entries from routes.json and return it"""
    # Save the path of shapes.json as a variable
    file_path = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files", "routes.json")
    # Open the file and load it as a dictionary
    f = open(file_path, encoding="utf-8-sig")
    routes_dict = json.load(f)
    # Now we can just return this dictionary version of the json file
    return JsonResponse(routes_dict)

def get_shapes_by_route(request, route_id):
    """
    View that returns an json object containing all objects
    from the shapes.json file where it matches our given route_id
    """
    base = settings.BASE_DIR
    # Save the path of shapes.json as a variable
    file_path = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files", "shapes.json")
    # Open the file and load it as a dictionary
    f = open(file_path, encoding="utf-8-sig")
    shapes_dict = json.load(f)

    # Create an a dictionary which will hold only the entries from shapes_dict that match our given route_id
    returnable_data = {}
    for id, data in shapes_dict.items():
        # Check if the route id matches the shape id and if so add it to our new dictionary as a key, value pair
        if data["shape_id"].split(".")[0] == route_id:
            returnable_data[id] = data
    return JsonResponse(returnable_data)

def get_direction_bus(request, data):
    """Direction function called here"""

    # Loads json data passed from the request - obtained from google maps api
    data = json.loads(data)
    print("original-data",data)
    data_return = {}
    data_return["route"] = []
    data_return["departure_time"] = []
    data_return["arrival_time"] = []
    for bus in range(0,len(data["departure_times"])):
        # Calls setting data to see can our own predictive models be used for any given bus route
        temporary_dict = setting_data(data["departure_times"][bus],data["departure_stops"][bus],data["arrival_stops"][bus],data["route_names"][bus], data["date_time"])
        data_return["route"].append(temporary_dict["route"][0])
        # If returned data contains gmaps or a predictive timestamp appends to data being returned to frontend
        if temporary_dict["departure_time"][0] == "gmaps":
            data_return["departure_time"].append(temporary_dict["departure_time"][0])
        else:
            data_return["departure_time"].append(temporary_dict["departure_time"][0] * 1000)
        if temporary_dict["arrival_time"][0] == "gmaps":
            data_return["arrival_time"].append(temporary_dict["arrival_time"][0])
        else:
            data_return["arrival_time"].append(temporary_dict["arrival_time"][0] * 1000)
    print("data_returned",data_return)
    # Catch if departure time before arrival time of previous bus, applies gmaps to return a google prediction
    if len(data_return["departure_time"]) >1:
        for departure_time in range(1,len(data_return["departure_time"])):
            # If departure time is greater then the previous arrival time applies google maps to try mitigate errors
            if data_return["departure_time"][departure_time] != "gmaps" and data_return["arrival_time"][departure_time-1] != "gmaps" and int(data_return["departure_time"][departure_time]) <int(data_return["arrival_time"][departure_time-1]):
                for depBefArr in range(0,len(data_return["departure_time"])):
                    data_return["departure_time"][depBefArr] = "gmaps"
                    data_return["arrival_time"][depBefArr] = "gmaps"
                print("bad times")
    return JsonResponse(data_return)

def timetable_main(request):
    """ list of all timetables """

    file_path_route = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files",
                                   "routes.json")
    routes_dict = open(file_path_route, encoding="utf-8-sig")
    return render(request, 'dublinBus/Timetable_main.html', {"routes" : routes_dict})

def timetable_route(request):
    """Returns the json file for routes.json"""

    file_path_route = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files",
                                   "routes.json")
    f = open(file_path_route, encoding="utf-8-sig")
    routes_dict = json.load(f)
    f.close()
    return JsonResponse(routes_dict)

def timetable(request, route):
    """Returns values from the database to form the individual timetable"""

    print(route)
    route_num = list(route.split(":"))[0]
    headsign = list(route.split(":"))[1].strip()
    results = Current_timetable_all.objects
    result = list(results.filter(route=route_num, headsign=headsign).order_by("day","stop","stop_time").values("stop","stop_time","day"))
    result_list = json.dumps(result)
    return render(request, 'dublinBus/timetables.html', {"result": result_list})

def setting_data(dep_time,dep_stop,arr_stop,route_name,date_time):
    """Converts the google suggestion returned to the backend into Local model
    Based upon our local pickle files, data within the database and json files"""

    # Splits the route name as gives headsign with number--[number: headsign]
    route = list(route_name.split(":"))
    data_return = {}
    # Opens given timetable for route provided from frontend
    file_path_times = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files",
                                   "bus_times", route[0] + "_timetable.json")
    if os.path.isfile(file_path_times) == True:
        f = open(file_path_times, encoding="utf-8-sig")
        times_dict = json.load(f)
        f.close()
    else:
        data_return["route"] = ["gmaps"]
        data_return["departure_time"] = ["gmaps"]
        data_return["arrival_time"] = ["gmaps"]
        return data_return
    # Opens routes.json
    file_path_route = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files",
                                   "routes.json")
    f = open(file_path_route, encoding="utf-8-sig")
    routes_dict = json.load(f)
    f.close()
    file_path = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files", "stops.json")
    f = open(file_path, encoding="utf-8-sig")
    stop_dict = json.load(f)
    f.close()
    depart_time = list(dep_time.split(":"))
    print(depart_time)
    date = datetime.fromtimestamp(int(date_time)) - relativedelta(months=1)
    print(date)
    month = date.month
    year = date.year
    hour = date.hour
    min = date.minute
    weekday = date.weekday()
    date = date.day
    if weekday <5:
        predict_day = "mon"
    elif weekday ==5:
        predict_day = "sat"
    elif weekday ==6:
        predict_day = "sun"
    # time is given in form of HH:MM am/pm checks if am or pm
    if depart_time[-1][-2:] == "pm" or (int(depart_time[0])>=12 and "am" not in depart_time[-1]):
        # Changes pm to HH:MM:SS format matches that in timetable
        if int(depart_time[0]) >= 12:
            time_dir = str(depart_time[0]) + ":" + depart_time[1][:2] + ":00"
        else:
            hh = 12 + int(depart_time[0])
            time_dir =str(hh) + ":" + depart_time[1][:2] + ":00"
    # Format if it contains am or less than and equal to 12, formats to 24 hour format
    elif depart_time[-1][-2:] == "am" or (int(depart_time[0])<=12):
        hh =int(depart_time[0])
        if hh < 10:
            time_dir = "0" + str(hh) + ":" + depart_time[1][:2] + ":00"
        elif hh == 12:
            time_dir = "0" + str(hh - 12) + ":" + depart_time[1][:2] + ":00"
        else:
            time_dir =str(hh) + ":" + depart_time[1][:2] + ":00"
    # Gets the stop number if available for departure and arrival if none available compares to stops.json
    last_stop = None
    try:
        if (list(dep_stop.split(" "))[-1]).isnumeric() == True:
            depart_stop = list(dep_stop.split(" "))[-1]
            for bus_route_stops in range(0, len(stop_dict[depart_stop]["routes"])):
                if route[1].strip(" ") == stop_dict[depart_stop]["routes"][bus_route_stops][1] and route[0].strip(" ") == stop_dict[depart_stop]["routes"][bus_route_stops][0]:
                    # gets distance along route and last stop
                    distance_depart = stop_dict[depart_stop]["routes"][bus_route_stops][3]
                    last_stop = stop_dict[depart_stop]["routes"][bus_route_stops][5]
                    break
                if len(stop_dict[depart_stop]["routes"]) -1 == bus_route_stops and last_stop == None:
                    distance_depart = 0
                    dep_stop_list = []
                    depart_stop = None
                    for i in stop_dict:
                        # Checks for stop when stop name == departure name
                        if stop_dict[i]["stop_name"] == dep_stop or stop_dict[i]["stop_name"] in dep_stop:
                            # Acquires the distance percent and last stop when found
                            dep_stop_list.append(i)
                            for bus_route_stops in range(0, len(stop_dict[i]["routes"])):
                                if route[1].strip(" ") == stop_dict[i]["routes"][bus_route_stops][1] and distance_depart <= stop_dict[i]["routes"][bus_route_stops][3] and route[0].strip(" ") == stop_dict[i]["routes"][bus_route_stops][0]:
                                    depart_stop = i
                                    distance_depart = stop_dict[i]["routes"][bus_route_stops][3]
                                    last_stop = stop_dict[i]["routes"][bus_route_stops][5]
        else:
            # If no stop number was available for departure checks by name
            distance_depart = 0
            dep_stop_list = []
            depart_stop = None
            for i in stop_dict:
                # Checks for stop when stop name == departure name
                if stop_dict[i]["stop_name"] == dep_stop or stop_dict[i]["stop_name"] in dep_stop:
                    # Acquires the distance percent and last stop when found
                    dep_stop_list.append(i)
                    for bus_route_stops in range(0, len(stop_dict[i]["routes"])):
                        if route[1].strip(" ") == stop_dict[i]["routes"][bus_route_stops][1] and distance_depart <=stop_dict[i]["routes"][bus_route_stops][3] and route[0].strip(" ") == stop_dict[i]["routes"][bus_route_stops][0]:
                            depart_stop = i
                            distance_depart = stop_dict[i]["routes"][bus_route_stops][3]
                            last_stop = stop_dict[i]["routes"][bus_route_stops][5]
        #Catch for if the Name check couldn't find the correct stop departure and arrival
        if depart_stop == None or last_stop ==None:
            data_return["route"] = ["gmaps"]
            data_return["departure_time"] = ["gmaps"]
            data_return["arrival_time"] = ["gmaps"]
            return data_return
        # If stop number is contained within the retrieved data from the frontend for arrival stop
        if (list(arr_stop.split(" "))[-1]).isnumeric() == True:
            arr_stop = list(arr_stop.split(" "))[-1]
            for bus_route_stops in range(0, len(stop_dict[arr_stop]["routes"])):
                if route[1].strip(" ") == stop_dict[arr_stop]["routes"][bus_route_stops][1]:
                    distance_arr = stop_dict[arr_stop]["routes"][bus_route_stops][3]
        # Else attempts to match the name of the stop with our local json files
        else:
            for i in stop_dict:
                if stop_dict[i]["stop_name"] == arr_stop or stop_dict[i]["stop_name"] == list(arr_stop.split(","))[-1].strip(" "):
                    for bus_route_stops in range(0, len(stop_dict[i]["routes"])):
                        if route[1].strip(" ") == stop_dict[i]["routes"][bus_route_stops][1]:
                            arr_stop = i
                            distance_arr = stop_dict[i]["routes"][bus_route_stops][3]
        # if departure stop in timetable for route given
        if route[1].strip(" ") in times_dict:
            if depart_stop in times_dict[route[1].strip(" ")][predict_day]:
                # Gets the next time scheduled after given time
                for timetable_time in range(0, len(times_dict[route[1].strip(" ")][predict_day][depart_stop])):
                    if time_dir < times_dict[route[1].strip(" ")][predict_day][depart_stop][timetable_time][1]:
                        next_bus = times_dict[route[1].strip(" ")][predict_day][depart_stop][timetable_time][0]
                        break
        # Finds the headsign for bus route to check if inbound or outbound
        for headsign in range(0, len(routes_dict[route[0]]["direction"])):
            if routes_dict[route[0]]["direction"][headsign][0] == route[1].strip(" "):
                direction = routes_dict[route[0]]["direction"][headsign][1]
                # Inbound == 2, Outbound ==1
                if direction == "I":
                    direction = 2
                else:
                    direction = 1
        entry = 0
        while times_dict[route[1].strip(" ")][predict_day][last_stop][entry][0] != next_bus:
            entry += 1
        last_stop_time = times_dict[route[1].strip(" ")][predict_day][last_stop][entry][1]
        h, m, s = next_bus.split(':')
        # departure time in mins
        next_bus_min = int(h) * 60 + int(m)
        h, m, s = last_stop_time.split(':')
        # arrival time in mins
        last_stop_min = int(h) * 60 + int(m)
        # Find range of for timestamp: -1 hour to +2 hours from given time range of times in forecast model
        if hour - 1 < 0:
            timestamp_cur_bef = datetime(year, month, date - 1, 23, min, 0)
        else:
            timestamp_cur_bef = datetime(year, month, date, hour - 1, min, 0)
        if hour + 2 >= 24:
            timestamp_cur_aft = datetime(year, month, date + 1, hour - 22, min, 0)
        else:
            timestamp_cur_aft = datetime(year, month, date, hour + 2, min, 0)
        print(timestamp_cur_bef)
        print(timestamp_cur_aft)
        timestamp_cur_bef = datetime.timestamp(timestamp_cur_bef)
        timestamp_cur_aft = datetime.timestamp(timestamp_cur_aft)
        print(timestamp_cur_bef)
        print(timestamp_cur_aft)

        results = WeatherForecast.objects.filter(timestamp__lte=timestamp_cur_aft,timestamp__gt=timestamp_cur_bef).values()
        if not results:
            print("no weather")
            prediction = predict(route[0], direction, last_stop_min, next_bus_min, actual_dep=next_bus_min, month=month,
                                 date=date)
        else:
            # change temp to celcius
            temp = results[0]["main_temp"] - 273.15
            weather_id = results[0]["weather_id"]
            print(date)
            print(route[0], direction, last_stop_min, next_bus_min, month, date)
            prediction = predict(route[0], direction, last_stop_min, next_bus_min, actual_dep=next_bus_min, month=month,
                                 date=date, temp=temp, weather=weather_id)
        print(prediction)
        if prediction == False or prediction < next_bus_min:
            print("prediction failed")
            data_return["route"] = ["gmaps"]
            data_return["departure_time"] = ["gmaps"]
            data_return["arrival_time"] = ["gmaps"]

        else:
            # full time is the number of predicted minutes of the full route result from the database
            full_time = prediction - next_bus_min
            # Gets the amount of minutes taken to reach the departure stop
            predict_dep_mins = full_time * distance_depart
            predict_dep_mins = int(predict_dep_mins + next_bus_min)
            # Gets the amount of minutes taken to reach the arrival stop
            predict_dep_arr = full_time * (distance_arr)
            predict_dep_arr = int(predict_dep_arr + next_bus_min)
            # +1 month for javascript datetime, change min format to hours and min
            timestamp_return_dep = datetime(year, month, date, math.floor(predict_dep_mins / 60), predict_dep_mins % 60,0)
            timestamp_return_arr = datetime(year, month, date, math.floor(predict_dep_arr / 60), predict_dep_arr % 60,0)
            data_return["route"] = [route[0]]
            data_return["departure_time"] = [datetime.timestamp(timestamp_return_dep)]
            data_return["arrival_time"] = [datetime.timestamp(timestamp_return_arr)]
        return data_return
    except:
        data_return["route"] = ["gmaps"]
        data_return["departure_time"] = ["gmaps"]
        data_return["arrival_time"] = ["gmaps"]
        return data_return

def get_next_four_bus(request, stop):
    """Filters through buses in the next hour for a given stop
    Returns the next 4 buses based upon our prediction"""
    start_time = time.time()
    #Opens Path to stops.json / routes.json
    file_path = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files", "stops.json")
    file_path_route = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files", "routes.json")
    # Open the file and load it as a dictionary
    f = open(file_path, encoding="utf-8-sig")
    stop_dict = json.load(f)
    f.close()
    f = open(file_path_route, encoding="utf-8-sig")
    routejson_dict = json.load(f)
    f.close()

    # Gets current time from swagger time API
    with urlopen("https://www.timeapi.io/api/Time/current/zone?timeZone=Europe/Dublin") as url:
        s = url.read()
        dub_t = json.loads(s)
    print(dub_t["dateTime"])
    # Remove extra unit on time to ensure we can change format to HH:MM:SS
    dub_date_time = dub_t["dateTime"][:-1]
    dub_date_time = datetime.strptime(dub_date_time.replace("T", " "), '%Y-%m-%d %H:%M:%S.%f')
    # current month as integer
    current_month=dub_date_time
    current_month =int(current_month.strftime("%m"))
    current = dub_date_time.time()
    current_time = current.strftime("%H:%M:%S")
    # Calculates current time in minutes from HH:MM:SS format
    current_time_mins = list(current_time.split(":"))
    current_time_mins = (int(current_time_mins[0])*60) +int(current_time_mins[1])
    # Obtains how far in the future we want buses called from currently 1 hour forward
    future_time = list(current_time.split(":"))
    if int(future_time[0]) == 23:
        future_time = "00:"+ future_time[1] + ":00"
    elif int(future_time[0]) >= 9:
        future_time = str(int(future_time[0]) +1) + ":" + future_time[1] + ":00"
    else:
        future_time = "0" + str(int(future_time[0]) +1) + ":" + future_time[1] + ":00"
    # Current day to check and match Json files format
    Current_Day = dub_date_time.strftime("%A")
    if Current_Day == "Saturday":
        Current_Day = "sat"
    elif Current_Day == "Sunday":
        Current_Day = "sun"
    else:
        Current_Day = "mon"
    routes = []
    distance = []
    in_out = []
    headsign_list =[]
    headsign_list_2 = []
    buses = []
    # loops over list for a given stop of routes
    for bus_route in range(0, len(stop_dict[stop]["routes"])):
        # Appends routes, head-sign and distances for stop from stops.json
        routes.append(stop_dict[stop]["routes"][bus_route][0])
        headsign_list.append(stop_dict[stop]["routes"][bus_route][1])
        distance.append(stop_dict[stop]["routes"][bus_route][3])
        for direction in range (0, len(routejson_dict[stop_dict[stop]["routes"][bus_route][0]]["direction"])):
            # If head-sign from stops is in routes with that head-sign obtains direction and adds head-sign to a second list
            if stop_dict[stop]["routes"][bus_route][1] == routejson_dict[stop_dict[stop]["routes"][bus_route][0]]["direction"][direction][0]:
                in_out.append(routejson_dict[stop_dict[stop]["routes"][bus_route][0]]["direction"][direction][1])
                headsign_list_2.append(routejson_dict[stop_dict[stop]["routes"][bus_route][0]]["direction"][direction][0])
    # Gets times from timetable table on database with time within range and stop and day matching requested
    results = Current_timetable_all.objects
    real_time_bus = CurrentBus.objects
    result = list(results.filter(stop_time__lt=future_time, stop_time__gte=current_time, stop=stop, day=Current_Day))
    # Gets the most recent weather forecast
    weather_results = WeatherForecast.objects.all().values()[0]
    print(weather_results)
    for bus_stop_time in result:
        # Obtaining information on each returned element from the selectquery
        route = bus_stop_time.route
        leave_time = bus_stop_time.leave_t
        leave_time_mins = list(leave_time.split(":"))
        leave_time_mins = (int(leave_time_mins[0]) * 60) + int(leave_time_mins[1])
        arr_time = bus_stop_time.end_t
        arr_time_mins = list(arr_time.split(":"))
        arr_time_mins = (int(arr_time_mins[0]) * 60) + int(arr_time_mins[1])
        stop_time = bus_stop_time.stop_time
        stop_time_mins = list(stop_time.split(":"))
        stop_time_mins = (int(stop_time_mins[0]) * 60) + int(stop_time_mins[1])
        count=0
        count_2=0
        # Iterates through to find matching headsigns and bus route from Json to database
        while (routes[count] !=bus_stop_time.route and headsign_list[count] != bus_stop_time.headsign):
            predict_dis = distance[count]
            count+=1
        if count == 0:
            predict_dis = distance[count]
            count += 1
        # Checks the direction of the and converts to 1 or 2 as is needed for pickle files
        while headsign_list_2[count_2] !=bus_stop_time.headsign:
            predict_in_out = in_out[count_2]
            if predict_in_out == "I":
                predict_in_out_num = 2
            else:
                predict_in_out = "O"
                predict_in_out_num = 1
            count_2 +=1
        if count_2 ==0:
            predict_in_out = in_out[count_2]
            if predict_in_out == "I":
                predict_in_out_num = 2
            else:
                predict_in_out = "O"
                predict_in_out_num = 1
        # If no weather results still returns a solution with weather missing
        if not weather_results:
            prediction = predict(route, predict_in_out_num, arr_time_mins, leave_time_mins, month=current_month, date=dub_date_time.day)
        # Else gets prediction for that time and route
        else:
            temp = weather_results["main_temp"] - 273.15
            weather_id = weather_results["weather_id"]
            prediction = predict(route, predict_in_out_num, arr_time_mins, leave_time_mins, month=current_month,date=dub_date_time.day, temp=temp, weather=weather_id)
        if prediction == False:
            mins_till = stop_time_mins - current_time_mins
            if mins_till <0:
                pass
            else:
                buses.append([str(bus_stop_time.route + ": " + bus_stop_time.headsign), mins_till])
        else:
            # Prediction converted into time from now as an integer value
            prediction = int((prediction - arr_time_mins) * predict_dis)
            mins_till = (prediction + stop_time_mins) - current_time_mins
            if mins_till < 0:
                pass
            else:
                buses.append([str(bus_stop_time.route + ": " + bus_stop_time.headsign), mins_till])
    # Once all results have been checked sorts to find the top 4 results if available
    buses = sorted(buses, key=lambda x: x[1])[:4]
    print("--- %s seconds last ---" % (time.time() - start_time))
    return JsonResponse(buses, safe=False)

def predict(route, direction, arriv, dep, actual_dep=-1, month=-1, date=-1, temp=-273, weather=500):
    """To feed in prediction from the pickle file to various functions"""

    if month == -1:
        with urlopen("https://www.timeapi.io/api/Time/current/zone?timeZone=Europe/Dublin") as url:
            s = url.read()
            dub_t = json.loads(s)
        dub_date_time = dub_t["dateTime"][:-1]
        dub_date_time = datetime.strptime(dub_date_time.replace("T", " "), '%Y-%m-%d %H:%M:%S.%f')
        month = int(dub_date_time.strftime("%m")) - 1
    # If actual departure time not available sets to planned departure time
    if actual_dep == -1:
        actual_dep = dep
    # If no temp available sets based on 2020 average
    if temp == -273:
        # Average temperatures by month for ireland by month per https://www.met.ie/ for 2020
        temp_list = [6.1, 5.8, 6.3, 9.8, 12.0, 13.7, 13.8, 15.6, 13.0, 9.7, 8.1, 5.0]
        temp = temp_list[month]

    if date == -1:
        date = datetime.today().weekday()
    data = {
        'PLANNEDTIME_ARR': [arriv],  # float in minutes
        'PLANNEDTIME_DEP': [dep],  # float in minutes
        'ACTUALTIME_DEP': [actual_dep],  # float in minutes
        'temp': [temp],  # float in degrees, celcius obviously ;)
        'MONTH': [month],  # int as month (0 is January)
        'DAY': [date],  # int as day (0 is Monday)
        'weather_id': weather  # float as id relating to weather
    }

    # create dataframe
    X = pd.DataFrame.from_dict(data)
    # load model from file
    file_path_prediction = os.path.join(base, "dublinBus", "static", "dublinBus", "predictive_model","rfc_"+route+"_"+str(direction)+".pkl")
    if os.path.isfile(file_path_prediction)==True:
        with gzip.open(file_path_prediction, 'rb') as file:
            pkl = pickle.Unpickler(file)
            rfc = pkl.load()
        y = rfc.predict(X)
        return round(y[0], 2)
    else:
        return False
