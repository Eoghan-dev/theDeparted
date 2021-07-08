from django.contrib import admin
from dublinBus.models import CurrentWeather, CurrentBus, BusStops

admin.site.register(CurrentWeather)
admin.site.register(CurrentBus)
admin.site.register(BusStops)