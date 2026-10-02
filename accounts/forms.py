from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

import re
from django import forms
from django.forms import ModelForm

User = get_user_model()


class RegisterForm(UserCreationForm):

    # додаткові правила для полів при заповненні форми
    def clean_username(self):
        username = super().clean_username()

        if not re.fullmatch(r'[a-zA-Z][a-zA-Z0-9_-]{3,20}', username):
            raise forms.ValidationError(
                'Логін має починатися з латинської літери та містити '
                'від 4 до 21 символу: латинські літери, цифри, _ або -.'
            )

        return username

    def clean_email(self):
        email = self.cleaned_data['email']

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                'Користувач із такою електронною поштою вже існує.'
            )
        return email

    def clean_password1(self):
        password = self.cleaned_data["password1"]

        if not re.fullmatch(r'(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])[a-zA-Z0-9@$!%*?&]{8,}', password):
            raise forms.ValidationError(
                'Пароль має містити щонайменше 8 символів, '
                'велику й малу латинські літери та цифру. '
                'Дозволені спецсимволи: @$!%*?&.'
            )
        return password

    # required fields in form
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'role']
        labels = {
            'first_name': "Ім'я",
            'last_name': 'Прізвище',
            'username': 'Логін',
            'email': 'Електронна пошта',
            'role': 'Тип акаунта',
        }

class EditProfileForm(ModelForm):

    def clean_username(self):
        username = self.cleaned_data['username']

        if not re.fullmatch(r'[a-zA-Z][a-zA-Z0-9_-]{3,20}', username):
            raise forms.ValidationError(
                'Логін має починатися з латинської літери та містити '
                'від 4 до 21 символу: латинські літери, цифри, _ або -.'
            )

        return username

    def clean_email(self):
        email = self.cleaned_data['email']

        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(
                'Користувач із такою електронною поштою вже існує.'
            )
        return email

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']
        labels = {
            'first_name': "Ім'я",
            'last_name': 'Прізвище',
            'username': 'Логін',
            'email': 'Електронна пошта',
        }