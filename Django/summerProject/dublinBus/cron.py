from .models import WeatherForecast, CurrentBus
def weather_forecast():
    WeatherForecast.scrape()

def current_bus():
    CurrentBus.scrape()