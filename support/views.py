from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST

from support.forms import SupportContributionForm
from support.models import Need


@require_POST
def contribution(request, need_id):

    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Увійдіть, щоб надіслати підтвердження допомоги.',
            'redirect_url': reverse('accounts:login'),
        }, status=401)


    need = get_object_or_404(Need, pk=need_id)

    if not need.can_accept_contributions:
        return JsonResponse({
            'success': False,
            'message': 'Ця потреба більше не приймає внески.',
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

