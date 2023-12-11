from django.urls import path

from . import views

urlpatterns = [
    path("overview/", views.overview_view, name="overview_view"),
    path("details/<uuid:sat_data_id>/", views.details_view, name="details_view"),
    path("upload/", views.upload_view, name="upload_view"),
]