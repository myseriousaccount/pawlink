from django import forms
from .models import Shelter

class ShelterForm(forms.ModelForm):
    class Meta:
        model = Shelter
        fields = [
            'name', 'description', 'city', 'address',
            'delivery_service', 'delivery_branch',
            'phone', 'email', 'website', 'logo',
        ]
