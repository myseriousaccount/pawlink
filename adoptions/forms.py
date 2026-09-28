from django import forms
from .models import AdoptionApplication

class AdoptionApplicationForm(forms.ModelForm):


    class Meta:
        model = AdoptionApplication
        fields = ["message"]
        widgets = {
            'message': forms.Textarea(
                attrs={
                    'placeholder': "Розкажіть про себе: у якому місті живете, чи маєте досвід догляду за тваринами та в яких умовах житиме улюбленець. Чому хочете прихистити саме цю тварину? Залиште номер телефону або інший зручний спосіб зв’язку."
                }),
        }
