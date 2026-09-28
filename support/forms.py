from django import forms
from pathlib import Path
from PIL import Image
from io import BytesIO
import pypdf
from pypdf.errors import PdfReadError

from .models import Need, SupportContribution

class NeedForm(forms.ModelForm):
    class Meta:
        model = Need
        fields = ['name', 'description', 'category', 'frequency', 'target_amount', 'unit', 'is_active']

class SupportContributionForm(forms.ModelForm):
    class Meta:
        model = SupportContribution
        fields = ['amount', 'proof']
        labels = {
            'amount': 'Обсяг наданої допомоги',
            'proof': 'Файл підтвердження',
        }
        help_texts = {
            'amount': 'Вкажіть суму або кількість наданої допомоги.',
            'proof': 'Додайте квитанцію, чек або фото. Формати: PDF, JPG, JPEG, PNG. Максимальний розмір – 5 МБ',
        }
        error_messages = {
            'amount': {
                'required': 'Вкажіть обсяг наданої допомоги.',
                'invalid': 'Введіть коректне число.',
                'min_value': 'Значення має бути не меншим за 0,01.',
            },
            'proof': {
                'required': 'Додайте файл підтвердження.',
                'empty': 'Вибраний файл порожній. Виберіть інший.',
            },
        }

    # перевірка завантажених зображень
    def clean_proof(self):
        proof = self.cleaned_data['proof']

        if proof.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Файл завеликий. Максимальний розмір – 5 МБ.")

        extension = Path(proof.name).suffix.lower()
        if extension in ('.jpg', '.jpeg', '.png'):
            try:
                with Image.open(BytesIO(proof.read())) as image:
                    expected_format = 'PNG' if extension == '.png' else 'JPEG'

                    if image.format != expected_format:
                        raise forms.ValidationError(
                            'Вміст файлу не відповідає його розширенню.'
                        )

                    image.verify()

            except (OSError, SyntaxError, ValueError, Image.DecompressionBombError):
                raise forms.ValidationError(
                    'Не вдалося прочитати зображення. Виберіть коректний JPG або PNG.'
                )

            finally:
                proof.seek(0)

        elif extension == '.pdf':
            try:
                reader = pypdf.PdfReader(proof)

                if reader.is_encrypted:
                    raise forms.ValidationError(
                        'Завантажте PDF без шифрування та захисту паролем.'
                    )

                if len(reader.pages) == 0:
                    raise forms.ValidationError(
                        'PDF не містить сторінок. Виберіть інший файл.'
                    )

            except (PdfReadError, OSError, ValueError):
                raise forms.ValidationError(
                    'Не вдалося прочитати PDF. Файл пошкоджений або має неправильний формат.'
                )

            finally:
                proof.seek(0)

        return proof
