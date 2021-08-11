from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import CustomUser

class RegistrationForm(UserCreationForm):
    class Meta:
        """This is required to save to the User database with the updated form"""
        model = CustomUser
        fields=["username", "email", "first_name", "last_name", "password1", "password2"]
