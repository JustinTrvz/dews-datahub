from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm

from sat_data.models import SatData
from dews.settings import VERSION


def home_view(request):
    if not request.user.is_authenticated:
        return redirect("login_view")
    
    return dashboard_view(request)


def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect("login_view")

    total_sat_data = SatData.objects.count()
    total_users = User.objects.count()

    context = {
        "version": VERSION,
        "total_sat_data": total_sat_data,
        "total_users": total_users,
    }

    return render(request, "dashboard_view.html", context)
