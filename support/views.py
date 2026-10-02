from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import When, Case, IntegerField
from django.http import JsonResponse, Http404
from django.http import FileResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from animals.models import Animal
from shelters.models import Shelter
from support.forms import SupportContributionForm, NeedForm
from support.models import Need, SupportContribution


def manage_contributions(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Увійдіть, щоб переглянути підтвердження допомоги вашому притулку.')
        return redirect('accounts:login')

    if not request.user.is_shelter:
        raise PermissionDenied('Перегляд підтверджень допомоги доступний лише власникам притулків.')

    shelter = Shelter.objects.filter(owner=request.user).first()

    if shelter is None:
        messages.info(request, 'Спочатку створіть профіль притулку, щоб переглядати підтвердження допомоги.')
        return redirect('shelters:create_shelter')

    if not shelter.is_verified:
        raise PermissionDenied('Переглядати підтвердження допомоги може лише перевірений притулок.')

    contributions = (
        SupportContribution.objects
        .filter(need__animal__shelter=shelter)
        .annotate(
            review_priority=Case(
                When(
                    status=SupportContribution.ContributionStatus.PENDING,
                    then=0,
                ),
                default=1,
                output_field=IntegerField(),
            )
        )
        .order_by('review_priority', '-created_at')
    )

    return render(request, 'support/contributions_table.html', {
        'app': 'support',
        'title': 'Підтвердження допомоги',
        'contributions': contributions,
    })

def show_proof(request, contribution_id):
    if not request.user.is_authenticated:

        messages.info(request, 'Увійдіть, щоб переглянути підтвердження допомоги вашому притулку.')
        return redirect('accounts:login')

    if not request.user.is_shelter:
        raise PermissionDenied('Перегляд підтверджень допомоги доступний лише власникам притулків.')

    shelter = Shelter.objects.filter(owner=request.user).first()

    if shelter is None:
        messages.info(request, 'Спочатку створіть профіль притулку, щоб переглядати підтвердження допомоги.')
        return redirect('shelters:create_shelter')

    if not shelter.is_verified:
        raise PermissionDenied('Переглядати підтвердження допомоги може лише перевірений притулок.')

    contribution = get_object_or_404(
        SupportContribution,
        pk=contribution_id,
        need__animal__shelter=shelter)

    if not contribution.proof:
        raise Http404('Файл підтвердження не знайдено.')

    return FileResponse(
        contribution.proof.open('rb'),
        as_attachment=False
    )

@require_POST
def review_contribution(request, contribution_id):

    if not request.user.is_authenticated:
        messages.info(request, 'Увійдіть, щоб розглядати підтвердження допомоги вашому притулку.')
        return redirect('accounts:login')

    if not request.user.is_shelter:
        raise PermissionDenied('Розглядати підтвердження допомоги можуть лише власники притулків.')

    shelter = Shelter.objects.filter(owner=request.user).first()

    if shelter is None:
        messages.info(request, 'Спочатку створіть профіль притулку, щоб розглядати підтвердження допомоги.')
        return redirect('shelters:create_shelter')

    if not shelter.is_verified:
        raise PermissionDenied('Розглядати підтвердження допомоги може лише перевірений притулок.')

    contribution = get_object_or_404(
        SupportContribution,
        pk=contribution_id,
        need__animal__shelter=shelter)

    decision = request.POST.get('decision')

    if decision not in (
            SupportContribution.ContributionStatus.APPROVED,
            SupportContribution.ContributionStatus.REJECTED,
    ):
        messages.warning(request, 'Невідома дія. Статус підтвердження не змінено.')
        return redirect('support:manage_contributions')

    updated = SupportContribution.objects.filter(
        pk=contribution.pk,
        status=SupportContribution.ContributionStatus.PENDING,
    ).update(status=decision)

    if updated == 1:
        if decision == SupportContribution.ContributionStatus.APPROVED:
            messages.success(request, 'Підтвердження допомоги схвалено.')
        else:
            messages.success(request, 'Підтвердження допомоги відхилено.')
    else:
        messages.info(request, 'Це підтвердження допомоги вже розглянуто.')

    return redirect('support:manage_contributions')

@require_POST
def contribution(request, need_id):

    if not request.user.is_authenticated:
        messages.info(request, 'Увійдіть, щоб надіслати підтвердження допомоги.')
        return JsonResponse({
            'success': False,
            'redirect_url': reverse('accounts:login'),
        }, status=401)

    if request.user.is_shelter:
        return JsonResponse({
            'success': False,
            'message': 'Надсилати підтвердження допомоги можуть лише звичайні користувачі.',
        }, status=403)

    need = get_object_or_404(
        Need,
        pk=need_id,
        animal__shelter__status=Shelter.ShelterStatus.APPROVED,
    )

    if not need.can_accept_contributions:
        if need.unit == Need.Unit.MONEY and not need.animal.shelter.has_payment_details:
            message = 'Реквізити для грошової допомоги тимчасово недоступні.'
        else:
            message = 'Ця потреба більше не приймає внески.'
        return JsonResponse({
            'success': False,
            'message': message,
        }, status=409)

    form = SupportContributionForm(request.POST, request.FILES)

    if form.is_valid():

        contribution = form.save(commit=False)
        contribution.supporter = request.user
        contribution.need = need
        contribution.save()

        messages.success(
            request,
            'Підтвердження допомоги надіслано на перевірку.'
        )

        return JsonResponse({
            'success': True,
            'redirect_url': reverse(
                'animals:animal',
                args=(need.animal_id,)
            ),
        })
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors.get_json_data(),
        }, status=400)

def create_need(request, animal_id):

    if not request.user.is_authenticated:
        messages.info(request, 'Увійдіть, щоб додати потребу.')
        if request.method == 'POST':
            return JsonResponse({
                'success': False,
                'redirect_url': reverse('accounts:login'),
            }, status=401)
        return redirect('accounts:login')

    if not request.user.is_shelter:
        message = 'Додавати потреби можуть лише власники притулків.'
        if request.method == 'POST':
            return JsonResponse({'success': False, 'message': message}, status=403)
        raise PermissionDenied(message)

    shelter = Shelter.objects.filter(owner=request.user).first()
    if shelter is None:
        messages.info(request, 'Спочатку створіть профіль притулку, щоб додавати потреби.')
        if request.method == 'POST':
            return JsonResponse({
                'success': False,
                'redirect_url': reverse('shelters:create_shelter'),
            }, status=409)
        return redirect('shelters:create_shelter')

    if not shelter.is_verified:
        message = 'Додавати потреби може лише притулок зі статусом «Перевірений».'
        if request.method == 'POST':
            return JsonResponse({'success': False, 'message': message}, status=403)
        raise PermissionDenied(message)

    animal = get_object_or_404(Animal, pk=animal_id, shelter=shelter)

    if request.method == 'POST':
        form = NeedForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['unit'] == Need.Unit.MONEY and not shelter.has_payment_details:
                form.add_error(
                    'unit',
                    'Спочатку додайте отримувача та IBAN у профілі притулку.',
                )
            else:
                need = form.save(commit=False)
                need.animal = animal
                need.save()

                messages.success(
                    request,
                    f'Потребу «{need.name}» для тварини «{animal.name}» створено.',
                )

                return JsonResponse({
                    'success': True,
                    'redirect_url': reverse('animals:animal', args=[animal.pk]),
                })

        return JsonResponse({
            'success': False,
            'errors': form.errors.get_json_data(),
        }, status=400)

    else:
        form = NeedForm()

    return render(request, 'support/need_form.html', {
        'form': form,
        'title': f'Додати потребу для «{animal.name}»',
        'form_description': 'Вкажіть, яка допомога потрібна тварині, її цільовий обсяг і періодичність.',
        'submit_label': 'Створити потребу',
        'form_action': reverse('support:create_need', args=[animal.pk]),
        'has_payment_details': shelter.has_payment_details,
        'app': 'support',
    })
