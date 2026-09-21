from django import forms
from .models import Need, SupportContribution

class NeedForm(forms.ModelForm):
    class Meta:
        model = Need
        fields = ['name', 'description', 'category', 'frequency', 'target_amount', 'unit', 'is_active']

class SupportContributionForm(forms.ModelForm):
    class Meta:
        model = SupportContribution
        fields = ['amount', 'proof']