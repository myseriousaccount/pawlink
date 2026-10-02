from pathlib import Path

from django import forms
import re

from django.core.files.uploadedfile import UploadedFile

from .models import Shelter

class ShelterForm(forms.ModelForm):
    class Meta:
        model = Shelter
        fields = [
            'name', 'description', 'city', 'address',
            'delivery_service', 'delivery_branch',
            'payment_recipient', 'payment_iban',
            'phone', 'email', 'website', 'logo',
        ]
        help_texts = {
            'payment_recipient': 'Вкажіть ім’я або назву отримувача. Ці дані буде видно біля грошових потреб.',
            'payment_iban': 'Вкажіть український IBAN. Його буде видно біля грошових потреб.',
        }

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')

        if not isinstance(logo, UploadedFile):
            return logo

        if logo.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Файл завеликий. Максимальний розмір – 5 МБ.")

        extension = Path(logo.name).suffix.lower()
        if extension in ('.jpg', '.jpeg', '.png'):
            expected_format = 'PNG' if extension == '.png' else 'JPEG'

            if logo.image.format != expected_format:
                raise forms.ValidationError(
                    'Вміст файлу не відповідає його розширенню.'
                )

        else:
            raise forms.ValidationError('Дозволені формати: JPG і PNG')

        return logo

    def clean_payment_iban(self):
        iban = re.sub(r'\s+', '', self.cleaned_data['payment_iban']).upper()
        if iban:
            if not re.fullmatch(r'UA[0-9]{27}', iban):
                raise forms.ValidationError('Вкажіть український IBAN: UA та 27 цифр.')

            number = iban[4:] + '3010' + iban[2:4]
            if int(number) % 97 != 1:
                raise forms.ValidationError('Перевірте IBAN: контрольні цифри не збігаються.')

        return iban

    def clean(self):
        cleaned_data = super().clean()
        recipient = cleaned_data.get('payment_recipient')
        iban = cleaned_data.get('payment_iban')

        if recipient and not iban and 'payment_iban' not in self.errors:
            self.add_error('payment_iban', 'Вкажіть IBAN отримувача.')
        if iban and not recipient:
            self.add_error('payment_recipient', 'Вкажіть ім’я або назву отримувача.')

        return cleaned_data
