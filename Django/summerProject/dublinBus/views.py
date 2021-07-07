from django.shortcuts import render

from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.shortcuts import render, get_object_or_404
from .models import CurrentWeather, CurrentBus, bus_stops


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
    bus_stops.scrape()
    return HttpResponse("Finished scraping bus_stops, results saved to database!")

def get_bus_stops(request):
    """View to get all bus stops from our db and return it as json"""
    # Get all bus stops as an array of json objects
    bus_stops_json = list(bus_stops.objects.values())
    # return JsonResponse({"stops_data": bus_stops_json})
    return JsonResponse(bus_stops_json, safe=False)