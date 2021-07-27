from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    username = models.CharField(max_length=100, primary_key=True)
    email = models.EmailField(max_length=500)
    first_name = models.CharField(max_length=500)
    last_name = models.CharField(max_length=500)
    fare_status = models.CharField(max_length=500, blank=True) # Student/Adult/Free travel etc.
    leap_card = models.BooleanField(null=True) # Whether they have a leap card or not
    favourite_roues = models.TextField(blank=True) # store favourite route/routes as a comma seperated string

    def __str__(self):
        return self.username