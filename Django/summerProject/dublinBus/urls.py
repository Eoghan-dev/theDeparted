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
    # ex: /update_user
    path('update_user', views.updateUser, name='updateUser'),
    # ex: /update_user_routes
    path('update_user_routes', views.updateUserRoutes, name='updateUserRoutes'),
    # ex: /update_user_stops
    path('update_user_stops', views.updateUserStops, name='updateUserStops'),
    #ex: /myAccount/
    path('myAccount', views.myAccount, name='myAccount'),
    #ex: /scrape_bus_stops/
    path('scrape_bus_stops', views.scrape_bus_stops, name='scrape_bus_stops'),
    #ex: /get_bus_stops/
    path('get_bus_stops', views.get_bus_stops, name='get_bus_stops'),
    #ex: /get_shapes_by_route/60-1-b12-1/
    path('get_shapes_by_route/<str:route_id>', views.get_shapes_by_route, name='get_shapes_by_route'),
    #ex: /get_routes/
    path('get_routes', views.get_routes, name='get_routes'),
    #ex: /get_bus_json/
    path('get_bus_json', views.get_bus_json, name='get_bus_json'),
]