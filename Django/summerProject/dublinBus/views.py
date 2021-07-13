from django.shortcuts import render

from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.shortcuts import render, get_object_or_404
from .models import CurrentWeather, CurrentBus, BusStops
from django.conf import settings # This allows us to import base directory which we can use for read/write operations
import os
import json
base = settings.BASE_DIR

def index(request):
    """View to load the homepage of our application"""
    return render(request, 'dublinBus/index.html')

def journey(request):
    """View to load the journey page of our application"""
    return render(request, 'dublinBus/journey.html')

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
