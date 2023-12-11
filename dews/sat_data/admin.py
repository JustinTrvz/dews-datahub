from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(SatData)
admin.site.register(BandInfo)
admin.site.register(AreaInfo)
admin.site.register(ImageInfo)
admin.site.register(BoundLatitudes)
admin.site.register(CaptureInfo)
admin.site.register(Calculation)