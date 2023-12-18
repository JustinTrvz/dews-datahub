import logging
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from dews.settings import VERSION
from django.contrib.auth.forms import UserCreationForm

logger = logging.getLogger("django")

def login_view(request):
    # User already logged in
    if request.user.is_authenticated:
        return redirect("dashboard_view")

    context = {
        "version": VERSION,
        "error": None,
    }

    # Authenticate user on POST request
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        remember_me = request.POST.get("remember_me")

        user = authenticate(request, username=username, password=password)
        logger.debug(f"User '{username}' is authenticated.")
        if not user is None:
            login(request, user)
            logger.debug(f"User '{username}' has logged in.")
            return redirect("dashboard_view")
        else:
            logger.debug(f"User '{username}' entered invalid username or password!")
            context["error"] = "Invalid username or password!"


    # Return login page on GET request
    return render(request, "login.html", context)

def logout_view(request):
    if request.method == "POST":
        logout(request)
        logger.debug(f"User '{request.user.username}' logged out.")
        return redirect("login_view")
    
    context = {
        "version": VERSION,
    }
    return render(request, "logout.html", context)

def register_view(request):
    # Create user on POST request
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            logger.debug(f"UserCreationForm is valid. request='{request}'")
            form.save()
            return redirect("login_view")
    # Return sign up page on GET request
    else:
        form = UserCreationForm()
        context = {
            "version": VERSION,
            "form": form,
        }
        return render(request, "register.html", context)