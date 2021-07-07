from django.urls import path

from . import views

urlpatterns = [
    # ex: /
    path('', views.index, name='index'),
    path('home', views.index, name='index'),
    path('journey', views.journey, name='journey'),
    # ex: /scrapeCW
    path('scrapeCW', views.scrapeCW, name='scrapeCW'),
    # ex: /scrapeCB
    path('scrapeCB', views.scrapeCB, name='scrapeCB'),
    #ex: /scrape_bus_stops/
    path('scrape_bus_stops', views.scrape_bus_stops, name='scrape_bus_stops'),
    #ex: /get_bus_stops/
    path('get_bus_stops', views.get_bus_stops, name='get_bus_stops')
]