from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST

from adoptions.forms import AdoptionApplicationForm
from adoptions.models import AdoptionApplication
from animals.models import Animal


@require_POST
def application(request, animal_id):

    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Увійдіть, щоб подати заявку на адопцію.',
            'redirect_url': reverse('accounts:login'),
        }, status=401)


    animal = get_object_or_404(Animal, pk=animal_id)

    if animal.adoption_status != Animal.Status.AVAILABLE:
        return JsonResponse({
            'success': False,
            'message': 'Неможливо подати заявку. Тварина вже усиновлена або ...',
        }, status=409)

    if request.user.is_shelter:
        return JsonResponse({
            'success': False,
            'message': 'Притулок не може подати заявку.',
        }, status=409)

    form = AdoptionApplicationForm(request.POST)

    if form.is_valid():

        adoption_application, created = AdoptionApplication.objects.get_or_create(
            user=request.user,
            animal=animal,
            defaults={
                'message': form.cleaned_data['message'],
            },
        )

        if not created:
            return JsonResponse({
                'success': False,
                'message': 'Ви вже подали заявку на цю тварину.',
            }, status=409)

        adoption_application.save()

        messages.success(request, 'Заявку надіслано.')

        return JsonResponse({
            'success': True,
            'message': 'Заявку надіслано.',
            'redirect_url': reverse('animals:animal', args=(animal.id,))
        })
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors.get_json_data(),
        }, status=400)

