from django.urls import path

from . import views

urlpatterns = [
    # ex: /dublinBus
    path('', views.index, name='index'),
    # ex: /dublinBus/scrapeCW
    path('scrapeCW', views.scrapeCW, name='scrapeCW'),
    # ex: /dublinBus/scrapeCB
    path('scrapeCB', views.scrapeCB, name='scrapeCB'),
    #ex: /dublinBus/2/
    path('<int:entry_id>/', views.detail, name='detail'),
    #ex: /dublinBus/scrape_bus_stops/
    path('scrape_bus_stops', views.scrape_bus_stops, name='get_bus_stops')
]