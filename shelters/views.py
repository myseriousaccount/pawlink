from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from shelters.forms import ShelterForm
from shelters.models import Shelter

def edit_shelter(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Увійдіть, щоб редагувати профіль притулку.')
        if request.method == 'POST':
            return JsonResponse({
                'success': False,
                'redirect_url': reverse('accounts:login'),
            }, status=401)
        return redirect('accounts:login')

    if not request.user.is_shelter:
        message = 'Редагувати профіль може лише користувач із роллю «Притулок».'
        if request.method == 'POST':
            return JsonResponse({'success': False, 'message': message}, status=403)
        raise PermissionDenied(message)

    shelter = Shelter.objects.filter(owner=request.user).first()

    if shelter is None:
        messages.info(request, 'Спочатку створіть профіль притулку, щоб його редагувати.')
        if request.method == 'POST':
            return JsonResponse({
                'success': False,
                'redirect_url': reverse('shelters:create_shelter'),
            }, status=404)
        return redirect('shelters:create_shelter')

    if request.method == 'POST':
        form = ShelterForm(request.POST, request.FILES, instance=shelter)

        if form.is_valid():
            if form.has_changed():
                form.save()
                messages.success(request, 'Зміни профілю притулку збережено.')
            else:
                messages.info(request, 'Дані профілю залишилися без змін.')

            return JsonResponse({
                'success': True,
                'redirect_url': reverse('dashboard:shelter_dashboard')
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors.get_json_data(),
            }, status=400)

    else:
        form = ShelterForm(instance=shelter)

    return render(request, 'shelters/shelter_form.html', {
        'form': form,
        'title': 'Редагування профілю притулку',
        'form_description': 'Оновіть інформацію про притулок і контактні дані. Зміни збережуться одразу.',
        'submit_label': 'Зберегти зміни',
        'form_action': reverse('shelters:edit_shelter'),
        'app': 'shelters',
    })

def create_shelter(request):

    if not request.user.is_authenticated:
        messages.info(request, 'Увійдіть, щоб подати анкету притулку.')
        if request.method == 'POST':
            return JsonResponse({
                'success': False,
                'redirect_url': reverse('accounts:login'),
            }, status=401)
        return redirect('accounts:login')

    if not request.user.is_shelter:
        message = 'Подати анкету може лише користувач із роллю «Притулок».'
        if request.method == 'POST':
            return JsonResponse({'success': False, 'message': message}, status=403)
        raise PermissionDenied(message)

    if Shelter.objects.filter(owner=request.user).exists():
        if request.method == 'POST':
            return JsonResponse({
                'success': True,
                'redirect_url': reverse('dashboard:shelter_dashboard'),
            })
        return redirect('dashboard:shelter_dashboard')

    if request.method == 'POST':
        form = ShelterForm(request.POST, request.FILES)
        if form.is_valid():
            shelter = form.save(commit=False)
            shelter.owner = request.user
            shelter.save()

            messages.success(request, 'Анкету притулку надіслано на перевірку.')

            return JsonResponse({
                'success': True,
                'redirect_url': reverse('dashboard:shelter_dashboard')
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors.get_json_data(),
            }, status=400)

    else:
        form = ShelterForm()

    return render(request, 'shelters/shelter_form.html', {
        'form': form,
        'title': 'Анкета притулку',
        'form_description': 'Розкажіть про притулок і залиште контактні дані. Після надсилання адміністрація перевірить анкету.',
        'submit_label': 'Надіслати на перевірку',
        'form_action': reverse('shelters:create_shelter'),
        'app': 'shelters',
    })
