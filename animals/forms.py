from pathlib import Path
from django import forms
from .models import Animal, AnimalUpdate, AnimalImage
from django.core.files.uploadedfile import UploadedFile

class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = ["name", "age","sex", "species", "description", "adoption_status", "main_photo"]

    def clean_main_photo(self):
        main_photo = self.cleaned_data["main_photo"]

        # якщо під час редагування фото не поміняли то повернути його як є
        if not isinstance(main_photo, UploadedFile):
            return main_photo

        if main_photo.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Файл завеликий. Максимальний розмір – 5 МБ.")

        extension = Path(main_photo.name).suffix.lower()
        if extension in ('.jpg', '.jpeg', '.png'):
            expected_format = 'PNG' if extension == '.png' else 'JPEG'

            if main_photo.image.format != expected_format:
                raise forms.ValidationError(
                    'Вміст файлу не відповідає його розширенню.'
                )

        else:
            raise forms.ValidationError('Дозволені формати: JPG і PNG')

        return main_photo

class AnimalUpdateForm(forms.ModelForm):
    class Meta:
        model = AnimalUpdate
        fields = ["message"]

class AnimalImageForm(forms.ModelForm):
    class Meta:
        model = AnimalImage
        fields = ["image"]

    def clean_image(self):
        image = self.cleaned_data["image"]

        # якщо під час редагування фото не поміняли то повернути його як є
        if not isinstance(image, UploadedFile):
            return image

        if image.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Файл завеликий. Максимальний розмір – 5 МБ.")

        extension = Path(image.name).suffix.lower()
        if extension in ('.jpg', '.jpeg', '.png'):
            expected_format = 'PNG' if extension == '.png' else 'JPEG'

            if image.image.format != expected_format:
                raise forms.ValidationError(
                    'Вміст файлу не відповідає його розширенню.'
                )

        else:
            raise forms.ValidationError('Дозволені формати: JPG і PNG')

        return image