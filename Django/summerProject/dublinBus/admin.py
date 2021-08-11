from django.contrib import admin
from dublinBus.models import CurrentWeather, CurrentBus, BusStops, Current_timetable

admin.site.register(CurrentWeather)
admin.site.register(CurrentBus)
admin.site.register(BusStops)
admin.site.register(Current_timetable)