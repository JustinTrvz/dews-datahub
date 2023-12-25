from django import forms

from .models import SatData

class SatDataForm(forms.ModelForm):
    class Meta:
        model = SatData
        fields = ['archive']