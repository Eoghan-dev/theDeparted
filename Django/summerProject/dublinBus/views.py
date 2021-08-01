from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from .models import CurrentWeather, CurrentBus, BusStops
from django.conf import settings # This allows us to import base directory which we can use for read/write operations
import os
import json
import pandas as pd
import pickle
from datetime import timedelta
base = settings.BASE_DIR
from summerProject import DublinBus_current_info
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
import json
from datetime import datetime

def index(request):
    """View to load the homepage of our application"""
    if request.method == 'POST':
        route = request.POST.get("route")
        time = request.POST.get("time")
        route = predict_linear("56A",DIRECTION=1,PLANNEDTIME_ARR=30113.0,PLANNEDTIME_DEP=26400.0,ACTUALTIME_DEP=26365.0,temp=2.32,MONTH=2,weather_main='Clouds')
        route = timedelta(seconds=route)
    else:
        route = 0
    return render(request, 'dublinBus/index.html', {'route':route})

def journey(request):
    """View to load the journey page of our application"""
    return render(request, 'dublinBus/journey.html')

def myAccount(request):
    """View to load the accounts page of our application"""
    # If request was posted then a change was made to the password reset form on the page
    if request.method == 'POST':
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
    if request.user.is_authenticated:
        user = request.user
        # Get users fav routes and stops, convert to array and then convert to json so it can be passed as a context
        fav_routes = user.favourite_routes
        fav_routes_list = fav_routes.split(",")
        fav_routes_json = json.dumps(fav_routes_list)
        fav_stops = user.favourite_stops
        fav_stops_list = fav_stops.split(",")
        fav_stops_json = json.dumps(fav_stops_list)
    return render(request, 'dublinBus/myAccount.html', {'form': form, 'fav_routes': fav_routes_list, 'fav_stops': fav_stops_list})

def updateUser(request):
    """View to update user fare status and leap card from user settings page"""
    if request.method == "POST":
        # Get the values for fare_status and leap card
        fare_status = request.POST.get('fare_status_radios')
        leap_card_str = request.POST.get('leap_card_radios')
        # Parse the leap card string returned to get boolean
        if leap_card_str == "true":
            leap_card = True
        else:
            leap_card = False
        # Get the instance of our user model being used
        user = request.user
        # Make changes and save to db
        print("fare status", fare_status)
        print("leap card", leap_card)
        user.fare_status = fare_status
        user.leap_card = leap_card
        user.save()
        return render(request, 'dublinBus/myAccount.html')
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
                        # Convert back from list to comma seperated string
                        new_fav_routes = ",".join(fav_routes_list)
                        user.favourite_routes = new_fav_routes
                        user.save()
                        return redirect('myAccount')
    # If the route entered by the user wasn't found return an error
    return HttpResponse("Error, your inputted favourite route was not valid, please try again and make sure you select the full suggested route name")

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
            # Convert back from list to comma seperated string
            new_fav_stops = ",".join(fav_stops_list)
            user.favourite_stops = new_fav_stops
            user.save()
            return redirect('myAccount')
    # If the route entered by the user wasn't found return an error
    return HttpResponse("Error, your inputted favourite stop was not valid, please try again and make sure you select the full suggested route name")

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

def getRouteDepartureTime(request, route):
    """View to return the closest scheduled departure time for a certain bus route to the current time"""
    current_date_time = datetime.now()
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
        times = route_timetable['sat'].values()[0]
    elif current_day == 6:
        times = route_timetable['sun'].values()[0]
    else:
        times = route_timetable['mon'].values()[0]
    # Make an array with all the times converted to a datetime object (hours and minutes only)
    converted_times = list(map(lambda x: datetime.strptime(x, "%H:%M"), times))
    # Get current time as datetime object also with only hours and minutes
    now = datetime.now().strftime("%H:%M")
    now_dt = datetime.strptime(now, "%H:%M")
    # Remove all items from the timetable list that are before the current time as they're useless in this context
    filtered_times = list(filter(lambda x: x >= now_dt, converted_times))
    # Check if any times existed or if it's too late in the day
    if len(filtered_times) > 0:
        # Now find the closest match in filtered time to the current time
        closest_time = min(filtered_times, key=lambda dt: abs(dt - now_dt))
        # Extract the hour and minutes as a string and return it
        closest_time_str = closest_time.strftime("%H:%M:%S")
        return HttpResponse(closest_time_str)
    else:
        return HttpResponse("error")


def scrapeCW(request):
    """View to call our scrape method in the CurrentWeather class"""
    CurrentWeather.scrape()
    return HttpResponse("Finished scraping CurrentWeather, results saved to database!")

def scrapeCB(request):
    """View to call our scrape method in the CurrentBus class"""
    CurrentBus.scrape()
    return HttpResponse("Finished scraping CurrentBus, results saved to database!")

def scrape_bus_stops(request):
    """View to call our scrape method in the bus_stops class"""
    BusStops.scrape()
    return HttpResponse("Finished scraping bus_stops, results saved to database!")

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
    View that returns an json object containing all objects from the shapes.json file where it matches our given route_id
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

def predict_linear(ROUTEID,DIRECTION,PLANNEDTIME_ARR,PLANNEDTIME_DEP,ACTUALTIME_DEP,temp=10,MONTH=1,weather_main='Rain'):
    """
        View that returns an json object containing all objects from the shapes.json file where it matches our given route_id
        """
    base = settings.BASE_DIR
    # Save the path of shapes.json as a variable
    file_path = os.path.join(base, "dublinBus", "static","dublinBus", "predictive_model")
    weather = {'Clear': 0, 'Clouds': 1, 'Rain': 2, 'Mist': 3, 'Drizzle': 4, 'Snow': 5, 'Fog': 6}
    # features
    data = {
        'PLANNEDTIME_ARR': [PLANNEDTIME_ARR],
        'PLANNEDTIME_DEP': [PLANNEDTIME_DEP],
        'ACTUALTIME_DEP': [ACTUALTIME_DEP],
        'temp': [temp],
        'MONTH': [MONTH],
        'weather_main': [weather[weather_main]]
    }
    # create dataframe
    X = pd.DataFrame.from_dict(data)
    # load model from file
    with open(file_path+"\\" + str(ROUTEID) + '_' + str(DIRECTION) + '.pkl', 'rb') as file:
        model = pickle.load(file)
        # get prediction from model
    y = model.predict(X)
    # return the prediction
    return round(y[0][0])

def get_bus_json(request):
    """View to run the DublinBus_current_info scraper which gets json versions of our txt files for static bus"""
    DublinBus_current_info.main()
    return HttpResponse("Finished scraping bus_stops, results saved to database!")