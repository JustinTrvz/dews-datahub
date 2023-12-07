from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from sat_data.models import SatData

title = "DEWS-DataHub -"

def details_view(request, sat_data_id):
    sat_data = get_object_or_404(SatData, id=sat_data_id)
    context = {
        "title": f"{title} {sat_data.mission.capitalize()}-{sat_data.product_type.upper()}",
        "sat_data": sat_data
    }
    return render(request, "details_view.html", context)

def overview_view(request):
    context = {
        "title": f"{title} Satellite Data Overview",
        "sat_data_entries": SatData.objects.all()
    }
    return render(request, "overview_view.html", context)
