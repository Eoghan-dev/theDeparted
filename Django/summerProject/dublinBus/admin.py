from django.contrib import admin
from dublinBus.models import CurrentWeather, CurrentBus, bus_stops

admin.site.register(CurrentWeather)
admin.site.register(CurrentBus)
admin.site.register(bus_stops)