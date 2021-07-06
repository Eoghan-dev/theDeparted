from django.urls import path

from . import views

urlpatterns = [
    # ex: /dublinBus
    path('', views.index, name='index'),
    # ex: /dublinBus/login
    # path('login', views.login, name="login"),
    # ex: /dublinBus/scrapeCW
    path('scrapeCW', views.scrapeCW, name='scrapeCW'),
    # ex: /dublinBus/scrapeCB
    path('scrapeCB', views.scrapeCB, name='scrapeCB'),
    #ex: /dublinBus/scrape_bus_stops/
    path('scrape_bus_stops', views.scrape_bus_stops, name='scrape_bus_stops'),
    #ex: /dublinBus/get_bus_stops/
    path('get_bus_stops', views.get_bus_stops, name='get_bus_stops')
]