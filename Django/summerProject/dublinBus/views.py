from django.shortcuts import render

from django.http import HttpResponse
from django.template import loader
from .models import CurrentWeather


def index(request):
    CurrentWeatherList = CurrentWeather.objects.order_by('entry_id')[:5]
    template = loader.get_template('dublinBus/index.html')
    context = {
        'CurrentWeatherList': CurrentWeatherList,
    }
    return HttpResponse(template.render(context, request))

def scrapeCW(request):
    """View to call our scrape method in the CurrentWeather class."""
    CurrentWeather.scrape()
    return HttpResponse("Finished scraping, results saved to database!")