from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistrationForm

def register(request):
    """View to handle user registration using an extended version of the built in django form"""
    # Check if the request received was posted as that would mean it's a form submission so the form should be created with the data received
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        # save the new user in the database if the form is valid
        if form.is_valid():
            form.save()
            # Redirect back to homepage after user is created
            return redirect("/")
    # If form was not posted then nothing was submitted by user so just load an empty form
    else:
        form = RegistrationForm()
        return render(request, 'users/register.html', {"form": form})

def login(request):
    """View to handle user login"""
    # Check if the request was posted the same way we do in our register view
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        # Check if form is valid and re-direct if so
        if form.is_valid():
            return redirect("/")
    # If form was not posted then just load an empty form as we did in the register view
    else:
        form = AuthenticationForm()
        return render(request, 'users/register.html', {"form": form})