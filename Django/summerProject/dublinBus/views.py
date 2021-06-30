from django.shortcuts import render

from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, get_object_or_404
from .models import CurrentWeather, CurrentBus, bus_stops


def index(request):
    """Example view for the homepage which returns a dictionary of all entries in the CurrentWeather table"""
    currentWeatherList = CurrentWeather.objects.order_by('entry_id')
    template = loader.get_template('dublinBus/index.html')
    context = {
        'currentWeatherList': currentWeatherList,
    }
    return HttpResponse(template.render(context, request))

def detail(request, entry_id):
    """View that returns more detailed info for a row in the CurrentWeather table based on the entry_id"""
    # Get the appropriate object (row in table) according to the given entry id
    weatherEntry = get_object_or_404(CurrentWeather, pk=entry_id)
    context = {'weatherEntry': weatherEntry}
    return render(request, 'dublinBus/detail.html', context)

def scrapeCW(request):
    """View to call our scrape method in the CurrentWeather class"""
    CurrentWeather.scrape()
    return HttpResponse("Finished scraping CurrentWeather, results saved to database!")

def scrapeCB(request):
    """View to call our scrape method in the CurrentBus class"""
    CurrentBus.scrape()
    return HttpResponse("Finished scraping CurrentBus, results saved to database!")

def get_bus_stops(request):
    """View to call our scrape method in the bus_stops class, works by reading from txt file and saving to db"""
    bus_stops.scrape()
    return HttpResponse("Finished scraping bus_stops, results saved to database!")