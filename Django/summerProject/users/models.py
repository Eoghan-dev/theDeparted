from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    username = models.CharField(max_length=100, primary_key=True)
    email = models.EmailField(max_length=500)
    first_name = models.CharField(max_length=500)
    last_name = models.CharField(max_length=500)
    fare_status = models.CharField(max_length=500, blank=True, default="adult") # Student/Adult/Free travel etc.
    leap_card = models.BooleanField(default=False) # Whether they have a leap card or not
    favourite_routes = models.TextField(blank=True) # store favourite route/routes as a comma seperated string
    favourite_stops = models.TextField(blank=True)

    def __str__(self):
        return self.username