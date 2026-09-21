from django import forms
from .models import Animal, AnimalUpdate, AnimalImage

class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = ["name", "age", "species", "description", "adoption_status", "main_photo"]

class AnimalUpdateForm(forms.ModelForm):
    class Meta:
        model = AnimalUpdate
        fields = ["message"]

class AnimalImageForm(forms.ModelForm):
    class Meta:
        model = AnimalImage
        fields = ["image"]