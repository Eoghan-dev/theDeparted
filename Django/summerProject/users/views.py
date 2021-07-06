from django.shortcuts import render
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
def register(request):
    """View to load the login page of our application"""
    form = UserCreationForm
    return render(request, 'users/register.html', {"form": form})