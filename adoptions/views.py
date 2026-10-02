from django.utils import timezone

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Case, When, IntegerField
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from adoptions.forms import AdoptionApplicationForm
from adoptions.models import AdoptionApplication
from animals.models import Animal
from shelters.models import Shelter


@require_POST
def application(request, animal_id):

    if not request.user.is_authenticated:
        messages.info(request, 'Увійдіть, щоб подати заявку на адопцію.')
        return JsonResponse({
            'success': False,
            'redirect_url': reverse('accounts:login'),
        }, status=401)


    animal = get_object_or_404(Animal, pk=animal_id)

    if animal.adoption_status != Animal.Status.AVAILABLE:
        return JsonResponse({
            'success': False,
            'message': 'Ця тварина зараз не приймає заявки на адопцію.',
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
                'phone': form.cleaned_data['phone'],
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
            'redirect_url': reverse('animals:animal', args=(animal.id,))
        })
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors.get_json_data(),
        }, status=400)

# GET
def manage_applications(request):

    if not request.user.is_authenticated:
        messages.info(request, 'Увійдіть, щоб переглянути заявки на адопцію для вашого притулку.')
        return redirect('accounts:login')

    if not request.user.is_shelter:
        raise PermissionDenied('Перегляд заявок на адопцію доступний лише власникам притулків.')

    shelter = Shelter.objects.filter(owner=request.user).first()

    if shelter is None:
        messages.info(request, 'Спочатку створіть профіль притулку, щоб переглядати заявки на адопцію.')
        return redirect('shelters:create_shelter')

    if not shelter.is_verified:
        raise PermissionDenied('Переглядати заявки на адопцію може лише перевірений притулок.')

    applications = (
        AdoptionApplication.objects
        .filter(animal__shelter=shelter)
        .select_related('animal', 'user')
        .annotate(
            review_priority=Case(
                When(
                    status=AdoptionApplication.ApplicationStatus.PENDING,
                    then=0,
                ),
                When(
                    status=AdoptionApplication.ApplicationStatus.APPROVED,
                    then=1,
                ),
                default=2,
                output_field=IntegerField(),
            )
        )
        .order_by('review_priority', '-created_at')
    )

    return render(request, 'adoptions/adoptions_table.html', {
        'app': 'adoptions',
        'title': 'Заявки на адопцію',
        'applications': applications,
        'adoption_status_choices': Animal.Status.choices,
    })


@require_POST
def save_shelter_notes(request, application_id):

    if not request.user.is_authenticated:
        messages.info(request, 'Увійдіть, щоб зберегти нотатку до заявки.')
        return redirect('accounts:login')

    if not request.user.is_shelter:
        raise PermissionDenied('Зберігати нотатки до заявок можуть лише власники притулків.')

    shelter = Shelter.objects.filter(owner=request.user).first()

    if shelter is None:
        messages.info(request, 'Спочатку створіть профіль притулку, щоб зберігати нотатки до заявок.')
        return redirect('shelters:create_shelter')

    if not shelter.is_verified:
        raise PermissionDenied('Зберігати нотатки до заявок може лише перевірений притулок.')

    application = get_object_or_404(
        AdoptionApplication,
        pk=application_id,
        animal__shelter=shelter
    )

    if 'shelter_notes' not in request.POST:
        messages.warning(request, 'Не вдалося отримати текст нотатки.')
        return redirect('adoptions:manage_applications')

    shelter_notes = request.POST['shelter_notes'].strip()

    if application.shelter_notes == shelter_notes:
        messages.info(request, 'Нотатка не змінилася.')
        return redirect('adoptions:manage_applications')

    application.shelter_notes = shelter_notes
    application.save(update_fields=['shelter_notes', 'updated_at'])

    if shelter_notes:
        messages.success(request, 'Нотатку до заявки збережено.')
    else:
        messages.success(request, 'Нотатку до заявки видалено.')

    return redirect('adoptions:manage_applications')





@require_POST
def review_application(request, application_id):

    if not request.user.is_authenticated:
        messages.info(request, 'Увійдіть, щоб перевіряти заявки для вашого притулку.')
        return redirect('accounts:login')

    if not request.user.is_shelter:
        raise PermissionDenied('Перевіряти заявки можуть лише власники притулків.')

    shelter = Shelter.objects.filter(owner=request.user).first()

    if shelter is None:
        messages.info(request, 'Спочатку створіть профіль притулку, щоб перевіряти заявки.')
        return redirect('shelters:create_shelter')

    if not shelter.is_verified:
        raise PermissionDenied('Перевіряти заявки може лише перевірений притулок.')

    application = get_object_or_404(
        AdoptionApplication,
        pk=application_id,
        animal__shelter=shelter)

    decision = request.POST.get('decision')

    if decision not in (
            AdoptionApplication.ApplicationStatus.APPROVED,
            AdoptionApplication.ApplicationStatus.REJECTED,
    ):
        messages.warning(request, 'Невідома дія. Статус заявки не змінено.')
        return redirect('adoptions:manage_applications')

    shelter_comment = request.POST.get('comment', '').strip()
    if decision == AdoptionApplication.ApplicationStatus.REJECTED and not shelter_comment:
        messages.warning(request, 'Вкажіть причину відхилення заявки.')
        return redirect('adoptions:manage_applications')

    comment_to_save = (
        shelter_comment
        if decision == AdoptionApplication.ApplicationStatus.REJECTED
        else ''
    )

    if decision == AdoptionApplication.ApplicationStatus.APPROVED:
        expected_status = AdoptionApplication.ApplicationStatus.PENDING
        needs_available_animal = True
    elif application.status == AdoptionApplication.ApplicationStatus.PENDING:
        expected_status = AdoptionApplication.ApplicationStatus.PENDING
        needs_available_animal = False
    elif application.status == AdoptionApplication.ApplicationStatus.APPROVED:
        expected_status = AdoptionApplication.ApplicationStatus.APPROVED
        needs_available_animal = True
    else:
        messages.info(request, 'Цю заявку вже відхилено.')
        return redirect('adoptions:manage_applications')

    if needs_available_animal and not application.animal.is_available:
        messages.warning(request, 'Тварина більше не шукає домівку. Рішення щодо заявки не змінено.')
        return redirect('adoptions:manage_applications')

    applications_to_update = AdoptionApplication.objects.filter(
        pk=application.pk,
        status=expected_status,
    )
    if needs_available_animal:
        applications_to_update = applications_to_update.filter(
            animal__adoption_status=Animal.Status.AVAILABLE,
        )

    updated = applications_to_update.update(
        status=decision,
        shelter_comment=comment_to_save,
        updated_at=timezone.now(),
    )

    if updated == 1:
        if decision == AdoptionApplication.ApplicationStatus.APPROVED:
            messages.success(request, 'Заявку схвалено.')
        else:
            messages.success(request, 'Заявку відхилено.')
    else:
        messages.info(request, 'Статус заявки або тварини змінився. Оновіть сторінку.')

    return redirect('adoptions:manage_applications')
