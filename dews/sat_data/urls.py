from django.urls import path

from . import views

urlpatterns = [
    path("overview/", views.overview_view, name="overview_view"),
    path("details/<uuid:sat_data_id>/", views.sat_data_details_view, name="sat_data_details_view"),
    path("delete/<uuid:sat_data_id>/", views.sat_data_delete_view, name="sat_data_delete_view"),
    path("time_travel/details/<uuid:time_travel_id>/", views.time_travel_details_view, name="time_travel_details_view"),
    path("time_travel/delete/<uuid:time_travel_id>/", views.time_travel_delete_view, name="time_travel_delete_view"),
    path("upload/", views.sat_data_upload_view, name="sat_data_upload_view"),
    path("sentinel_hub/", views.sentinel_hub_request_view, name="sentinel_hub_request_view")
]