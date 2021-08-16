from django.urls import path

from . import views

urlpatterns = [
    # ex: /
    path('', views.index, name='index'),
    path('home', views.index, name='index'),
    path('update_user', views.updateUser, name='updateUser'),
    # ex: /add_user_routes
    path('add_user_route', views.addUserRoute, name='updateUserRoutes'),
    # ex: /add_user_stops
    path('add_user_stop', views.addUserStop, name='updateUserStops'),
    # ex: /del_user_route/56A
    path('del_user_route/<str:route>', views.delUserRoute, name="del_user_route"),
    #ex: /del_user_stop
    path('del_user_stop/<str:stop>', views.delUserStop, name="del_user_stop"),
    #ex: /myAccount/
    path('myAccount', views.myAccount, name='myAccount'),
    #ex: /get_bus_stops/
    path('get_bus_stops', views.get_bus_stops, name='get_bus_stops'),
    #ex: /get_shapes_by_route/60-1-b12-1/
    path('get_shapes_by_route/<str:route_id>', views.get_shapes_by_route, name='get_shapes_by_route'),
    #ex: /get_routes/
    path('get_routes', views.get_routes, name='get_routes'),
    #ex: /get_next_bus_time/56A:+Ringsend+road
    path('get_next_bus_time/<str:route>', views.get_next_bus_time, name='get_next_bus_time'),
    #ex: /get_direction_bus/
    path('get_direction_bus/<str:data>', views.get_direction_bus, name='get_direction_bus'),
    #ex: /get_prediction_for_stop/
    path('get_next_four_bus/<str:stop>', views.get_next_four_bus, name='get_next_four_bus'),
    # ex: /timetable/
    path('timetable', views.timetable_main, name='timetable_main'),
    # ex: /timetable/
    path('timetable_route/', views.timetable_route, name='timetable_route'),
    #ex: /timetable/
    path('timetable/<str:route>', views.timetable, name='timetable'),
    #ex: /dbTwitter/
    path('dbTwitter', views.dbTwitter, name='dbTwitter'),
    #ex: /aboutUs/
    path('aboutUs', views.aboutUs, name='aboutUs'),
]