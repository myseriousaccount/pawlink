from django import forms
from .models import AdoptionApplication

class AdoptionApplicationForm(forms.ModelForm):


    class Meta:
        model = AdoptionApplication
        fields = ['phone', 'message']
        widgets = {
            'phone': forms.TextInput(attrs={
                'type': 'tel',
                'autocomplete': 'tel',
                'placeholder': '+380…',
            }),
            'message': forms.Textarea(
                attrs={
                    'placeholder': "Розкажіть про себе: у якому місті живете, чи маєте досвід догляду за тваринами та в яких умовах житиме улюбленець. Чому хочете прихистити саме цю тварину?"
                }),
        }
        help_texts = {
            'phone': 'Необов’язково. Притулок зможе зателефонувати вам щодо заявки.',
        }
