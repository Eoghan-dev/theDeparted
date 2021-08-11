from .models import CurrentWeather
def run_scrapers():
    CurrentWeather.scrape()