from django.shortcuts import render

def login(request):
    """View to load the login page of our application"""
    return render(request, 'dublinBus/login.html')