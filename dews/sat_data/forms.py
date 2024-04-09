import logging

from django import forms
from django.contrib.gis.geos import GEOSGeometry
from django.core.exceptions import ValidationError

from .models import SatData, SHRequest


logger = logging.getLogger("django")


class SatDataForm(forms.ModelForm):
    class Meta:
        model = SatData
        fields = ['archive']


class SHRequestForm(forms.ModelForm):
    mission_choices = [
        ('', '---Select Mission---'),
        ('SENTINEL2_L1C', 'SENTINEL2_L1C'),
        ('SENTINEL2_L2A', 'SENTINEL2_L2A'),
    ]

    bands_choices = [
        ('AOT', 'AOT'),
        ('B01', 'B01'),
        ('B02', 'B02'),
        ('B03', 'B03'),
        ('B04', 'B04'),
        ('B05', 'B05'),
        ('B06', 'B06'),
        ('B07', 'B07'),
        ('B08', 'B08'),
        ('B8A', 'B8A'),
        ('B09', 'B09'),
        ('B11', 'B11'),
        ('B12', 'B12'),
        ('SCL', 'SCL'),
        ('TCI', 'TCI'),
        ('WVP', 'WVP'),
    ]

    resolution_choices = [
        (10, '10m'),
        (20, '20m'),
        (60, '60m'),
    ]

    metrics_choices = [
        ('ndvi', 'NDVI'),
        ('ndwi', 'NDWI'),
        ('evi', 'EVI'),
        ('smi', 'SMI'),
        ('rgb', 'RGB'),
    ]

    mission = forms.ChoiceField(
        choices=mission_choices,
        required=True,
    )
    bands = forms.MultipleChoiceField(
        choices=bands_choices,
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )
    resolution = forms.ChoiceField(
        choices=resolution_choices,
        widget=forms.Select(),
        required=True,
    )
    metrics_to_calc = forms.MultipleChoiceField(
        choices=metrics_choices,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True,
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
    )
    # Will be set via JavaScript
    coordinates = forms.CharField(
        widget=forms.HiddenInput(),
        required=True,
    )

    def clean_coordinates(self):
        coords = self.cleaned_data.get('coordinates')
        try:
            polygon = GEOSGeometry(coords)
            # Optionally, validate the polygon is indeed a Polygon
            if not polygon.geom_type == 'Polygon':
                raise ValueError
            return polygon
        except Exception as e:
            logger.error(f"Failed to clean coordinates. error='{e}'")
            raise ValidationError('Invalid polygon format.')

    class Meta:
        model = SHRequest
        fields = ['mission', 'resolution', 'metrics_to_calc', 'bands',
                  'start_date', 'end_date', 'coordinates']
