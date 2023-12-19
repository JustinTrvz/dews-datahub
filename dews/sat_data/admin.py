from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(TimeSeries)
admin.site.register(SatData)
admin.site.register(BandInfo)
admin.site.register(AreaInfo)
admin.site.register(IndexInfo)
admin.site.register(CaptureInfo)
