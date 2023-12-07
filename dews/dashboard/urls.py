from django.urls import path, include
from django.views.generic import RedirectView
from .views import dashboard_view

urlpatterns = [
    path('', RedirectView.as_view(url='/dashboard/', permanent=True), name='index_redirect'),
    path('dashboard/', dashboard_view, name='dashboard_view'),
]