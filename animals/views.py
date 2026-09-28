from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.http import require_POST

from adoptions.forms import AdoptionApplicationForm
from support.forms import SupportContributionForm
from animals.models import Animal


def animals_list(request):
    animals = Animal.objects.all()

    return render(request, 'animals/animals.html',context={
        'title': 'Тварини',
        'page': 'animals',
        'app': 'animals',
        'animals': animals
    })

def animal_detail(request, animal_id):
    animal = get_object_or_404(Animal, pk=animal_id)

    application_form = AdoptionApplicationForm()
    needs_with_forms = []
    for need in animal.needs.all():
        needs_with_forms.append({
            'need': need,
            'form': SupportContributionForm(
                auto_id=f'contribution_{need.id}_%s'
            ),
        })

    is_favorite = False

    if request.user.is_authenticated:
        is_favorite = animal.favorited_by.filter(
            pk=request.user.pk
        ).exists()


    return render(request, 'animals/animal.html',context={
        'title': 'Тварина',
        'page': 'animal',
        'app': 'animals',
        'animal': animal,
        'application_form': application_form,
        'needs': needs_with_forms,
        'is_favorite': is_favorite,
    })

@require_POST
def add_to_favorite(request, animal_id):

    if not request.user.is_authenticated:
        
        messages.info(
            request,
            'Увійдіть, щоб додати тварину в обране.'
        )

        return JsonResponse({
            'success': False,
            'redirect_url': reverse('accounts:login'),
        }, status=401)

    animal = get_object_or_404(Animal, pk=animal_id)

    is_favorite = animal.favorited_by.filter(
        pk=request.user.pk
    ).exists()

    if not is_favorite:

        animal.favorited_by.add(request.user)
        is_favorite = True
    else:
        animal.favorited_by.remove(request.user)
        is_favorite = False

    return JsonResponse({
        'success': True,
        'is_favorite': is_favorite,
    })
