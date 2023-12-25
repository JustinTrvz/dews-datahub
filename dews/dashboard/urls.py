from django.urls import path, include
from django.views.generic import RedirectView
import dashboard.views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path("", dashboard.views.dashboard_view, name="dashboard_view"),
]