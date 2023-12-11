from django import forms

from .models import SatData

class SatDataForm(forms.ModelForm):
    error_css_class = 'error-field'
    required_css_class = 'required-field'
    name = forms.CharField(max_length=100)
    archive = forms.FileField()

    class Meta:
        model = SatData
        fields = ['name', 'archive']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # django-crispy-forms
        for field in self.fields:
            new_data = {
                "placeholder": f'SatData {str(field).capitalize()}',
                "class": 'form-control',
                "hx-post": ".",
                "hx-trigger": "keyup changed delay:500ms",
                "hx-trigger": "keyup changed delay:500ms",
                "hx-target": "#recipe-container",
                "hx-swap": "outerHTML"
            }
            self.fields[str(field)].widget.attrs.update(
                new_data
            )
        self.fields['name'].label = ''
        self.fields['name'].widget.attrs.update({'class': 'form-control-2'})
        self.fields['archive'].widget.attrs.update({'rows': '2'})
