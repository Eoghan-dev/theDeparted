from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

class RegistrationForm(UserCreationForm):
    """Extended version of the built in user creation form which also takes in email and first/last names"""
    email = forms.EmailField(max_length=256, required=True)
    first_name = forms.CharField(max_length=256, required=True)
    last_name = forms.CharField(max_length=256, required=True)

    class Meta:
        """This is required to save to the User database with the updated form"""
        model = User
        fields=["email", "username", "first_name", "last_name", "password1", "password2"]
