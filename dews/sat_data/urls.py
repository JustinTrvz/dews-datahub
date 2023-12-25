from django.urls import path

from . import views

urlpatterns = [
    path("overview/", views.overview_view, name="overview_view"),
    path("details/<uuid:sat_data_id>/", views.sat_data_details_view, name="sat_data_details_view"),
    path("details/<uuid:time_travel_id>/", views.time_travel_details_view, name="time_travel_details_view"),
    path("upload/", views.sat_data_upload_view, name="sat_data_upload_view"),
]