from django.shortcuts import render
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
def login(request):
    """View to load the login page of our application"""
    form = UserCreationForm
    return render(request, 'users/login.html', {"form": form})