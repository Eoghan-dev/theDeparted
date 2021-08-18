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
            #log in
            username = request.POST['username']
            password = request.POST['password1']
            user = authenticate(username=username, password=password)

            if user is not None and user.is_active:
                # Correct password, and the user is marked "active"
                login(request, user)

            # Redirect back to homepage after user is created & logged in
            return redirect("/")
    # If form was not posted then nothing was submitted by user so just load an empty form
    else:
        form = RegistrationForm()
    return render(request, 'users/register.html', {"form": form})
