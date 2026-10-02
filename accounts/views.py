from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.views.decorators.http import require_POST

from .forms import RegisterForm, EditProfileForm
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.urls import reverse

# custom user model
User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            auth_login(request, new_user)

            messages.success(request, 'Реєстрація успішна')

            return JsonResponse({
                'success': True,
                'redirect_url': reverse('core:home')
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors.get_json_data(),
            }, status=400)
    else:
        # GET
        form = RegisterForm()

    return render(request, 'accounts/register.html', {
        'form': form,
        'title': 'Реєстрація',
        'app': 'accounts'
    })

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)

            messages.success(request, 'Вхід виконано успішно')

            return JsonResponse({
                'success': True,
                'redirect_url': reverse('core:home')
            })

        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors.get_json_data(),
            }, status=400)
    else:
        # GET
        form = AuthenticationForm(request)

    return render(request, 'accounts/login.html', {
        'form': form,
        'title': 'Вхід',
        'app': 'accounts'
    })

@login_required
@require_POST
def logout(request):
    auth_logout(request)
    messages.success(request, 'Ви вийшли з акаунта.')
    return redirect('accounts:login')

def edit_user(request):

    if not request.user.is_authenticated:
        messages.info(request, 'Увійдіть, щоб редагувати свій профіль.')
        if request.method == 'POST':
            return JsonResponse({
                'success': False,
                'redirect_url': reverse('accounts:login'),
            }, status=401)
        return redirect('accounts:login')

    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            if form.has_changed():
                form.save()
                messages.success(request, 'Зміни профілю збережено.')
            else:
                messages.info(request, 'Дані профілю залишилися без змін.')

            dashboard_url = (
                'dashboard:shelter_dashboard'
                if request.user.is_shelter
                else 'dashboard:user_dashboard'
            )
            return JsonResponse({
                'success': True,
                'redirect_url': reverse(dashboard_url)
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors.get_json_data(),
            }, status=400)

    else:
        form = EditProfileForm(instance=request.user)

    return render(request, 'accounts/user_form.html', {
        'form': form,
        'title': 'Редагування профілю користувача',
        'form_description': 'Оновіть інформацію про себе. Зміни збережуться одразу.',
        'submit_label': 'Зберегти зміни',
        'form_action': reverse('accounts:edit_user'),
        'app': 'accounts',
    })
