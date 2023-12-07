from django.shortcuts import render
from django.contrib.auth.models import User

from sat_data.models import SatData


def dashboard_view(request):
    total_sat_data = SatData.objects.count()
    total_users = User.objects.count()

    context = {
        'total_sat_data': total_sat_data,
        'total_users': total_users,
    }

    return render(request, 'dashboard_view.html', context)