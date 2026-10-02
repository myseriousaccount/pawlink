from django.contrib.auth.password_validation import password_changed
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.http import require_POST

from adoptions.forms import AdoptionApplicationForm
from animals.forms import AnimalForm, AnimalUpdateForm, AnimalImageForm
from shelters.models import Shelter
from support.forms import SupportContributionForm
from animals.models import Animal


def animals_list(request):
    animals = Animal.objects.filter(
        shelter__status=Shelter.ShelterStatus.APPROVED,
    ).exclude(adoption_status=Animal.Status.ARCHIVED)

    # фільтрація на сторінці
    species = request.GET.get('species', '').strip()
    city = request.GET.get('city', '').strip()

    if species:
        animals = animals.filter(species=species)
    if city:
        animals = animals.filter(shelter__city=city)

    return render(request, 'animals/animals.html',context={
        'title': 'Тварини',
        'page': 'animals',
        'app': 'animals',
        'animals': animals,
        'selected_species': species,
        'selected_city': city,
        'species_choices': Animal.Species.choices,
        'city_choices': Shelter.City.choices,
    })

def animal_detail(request, animal_id):
    animal = get_object_or_404(
        Animal,
        pk=animal_id,
        shelter__status=Shelter.ShelterStatus.APPROVED,
    )

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

    if request.user.is_authenticated and not request.user.is_shelter:
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
def change_animal_status(request, animal_id):

    if not request.user.is_authenticated:
        messages.info(
            request,
            'Увійдіть, щоб змінити статус тварини.'
        )

        return redirect('accounts:login')

    if not request.user.is_shelter:
        raise PermissionDenied('Змінювати статуси тварин можуть лише власники притулків.')

    shelter = Shelter.objects.filter(owner=request.user).first()
    if shelter is None:
        messages.info(request, 'Спочатку створіть профіль притулку, щоб змінювати статуси тварин.')
        return redirect('shelters:create_shelter')

    if not shelter.is_verified:
        raise PermissionDenied('Змінювати статуси тварин може лише перевірений притулок.')

    animal = get_object_or_404(Animal, pk=animal_id, shelter=shelter)
    return_to = (
        'adoptions:manage_applications'
        if request.POST.get('return_to') == 'applications'
        else 'animals:manage_animals'
    )
    adoption_status_choice = request.POST.get('adoption_status')
    if adoption_status_choice not in Animal.Status.values:
        messages.error(
            request, 'Оберіть статус зі списку.')
        return redirect(return_to)

    if animal.adoption_status == adoption_status_choice:
        messages.info(request, f'Статус тварини «{animal.name}» не змінився.')
        return redirect(return_to)

    animal.adoption_status = adoption_status_choice
    animal.save(update_fields=['adoption_status'])
    messages.success(
        request,
        f'Статус тварини «{animal.name}» змінено на «{animal.get_adoption_status_display()}».',
    )

    return redirect(return_to)

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

    if request.user.is_shelter:
        return JsonResponse({
            'success': False,
            'message':'Обране доступне лише звичайним користувачам.'
        }, status=403)

    animal = get_object_or_404(
        Animal,
        pk=animal_id,
        shelter__status=Shelter.ShelterStatus.APPROVED,
    )

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

def add_animal_image(request, animal_id):

    if not request.user.is_authenticated:
        messages.info(request, 'Увійдіть, щоб додати фото тварини.')
        if request.method == 'POST':
            return JsonResponse({
                'success': False,
                'redirect_url': reverse('accounts:login'),
            }, status=401)
        return redirect('accounts:login')

    if not request.user.is_shelter:
        message = 'Додавати фото тварин можуть лише власники притулків.'
        if request.method == 'POST':
            return JsonResponse({'success': False, 'message': message}, status=403)
        raise PermissionDenied(message)

    shelter = Shelter.objects.filter(owner=request.user).first()
    if shelter is None:
        messages.info(request, 'Спочатку створіть профіль притулку, щоб додавати фото тварин.')
        if request.method == 'POST':
            return JsonResponse({
                'success': False,
                'redirect_url': reverse('shelters:create_shelter'),
            }, status=404)
        return redirect('shelters:create_shelter')

    if not shelter.is_verified:
        message = 'Додавати фото тварин може лише перевірений притулок.'
        if request.method == 'POST':
            return JsonResponse({'success': False, 'message': message}, status=403)
        raise PermissionDenied(message)

    animal = get_object_or_404(Animal, pk=animal_id, shelter=shelter)

    if request.method == 'POST':
        form = AnimalImageForm(request.POST, request.FILES)

        if form.is_valid():
            image = form.save(commit=False)
            image.animal = animal
            image.save()
            messages.success(request, f'Фото для «{animal.name}» додано.')

            return JsonResponse({
                'success': True,
                'redirect_url': reverse('animals:animal', args=[animal.pk]),
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors.get_json_data(),
            }, status=400)

    else:
        form = AnimalImageForm()

    return render(request, 'animals/animal_form.html', {
        'form': form,
        'title': f'Додати фото для {animal.name}',
        'form_description': 'Оберіть фото у форматі JPG або PNG розміром до 5 МБ.',
        'submit_label': 'Додати фото',
        'form_action': reverse('animals:add_animal_image', args=[animal_id]),
        'app': 'animals',
    })

def create_animal_update(request, animal_id):

    if not request.user.is_authenticated:
        messages.info(request, 'Увійдіть, щоб додати оновлення про тварину.')
        if request.method == 'POST':
            return JsonResponse({
                'success': False,
                'redirect_url': reverse('accounts:login'),
            }, status=401)
        return redirect('accounts:login')

    if not request.user.is_shelter:
        message = 'Додати оновлення про тварину може лише користувач із роллю «Притулок».'
        if request.method == 'POST':
            return JsonResponse({'success': False, 'message': message}, status=403)
        raise PermissionDenied(message)

    shelter = Shelter.objects.filter(owner=request.user).first()
    if shelter is None:
        messages.info(request, 'Спочатку створіть профіль притулку, щоб додати оновлення про тварину.')
        if request.method == 'POST':
            return JsonResponse({
                'success': False,
                'redirect_url': reverse('shelters:create_shelter'),
            }, status=404)
        return redirect('shelters:create_shelter')

    if not shelter.is_verified:
        message = 'Додавати оновлення про тварину може лише перевірений притулок.'
        if request.method == 'POST':
            return JsonResponse({'success': False, 'message': message}, status=403)
        raise PermissionDenied(message)

    animal = get_object_or_404(Animal, pk=animal_id, shelter=shelter)

    if request.method == 'POST':
        form = AnimalUpdateForm(request.POST)

        if form.is_valid():
            update = form.save(commit=False)
            update.animal = animal
            update.save()
            messages.success(request, f'Оновлення про «{animal.name}» опубліковано.')

            return JsonResponse({
                'success': True,
                'redirect_url': reverse('animals:animal', args=[animal.pk]),
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors.get_json_data(),
            }, status=400)

    else:
        form = AnimalUpdateForm()

    return render(request, 'animals/animal_form.html', {
        'form': form,
        'title': f'Оновлення про {animal.name}',
        'form_description': 'Розкажіть, що нового у житті тварини.',
        'submit_label': 'Опублікувати оновлення',
        'form_action': reverse('animals:create_animal_update', args=[animal_id]),
        'app': 'animals',
    })

def create_animal(request):

    if not request.user.is_authenticated:
        messages.info(request, 'Увійдіть, щоб додати тварину.')
        if request.method == 'POST':
            return JsonResponse({
                'success': False,
                'redirect_url': reverse('accounts:login'),
            }, status=401)
        return redirect('accounts:login')

    if not request.user.is_shelter:
        message = 'Додавати тварин можуть лише власники притулків.'
        if request.method == 'POST':
            return JsonResponse({'success': False, 'message': message}, status=403)
        raise PermissionDenied(message)

    shelter = Shelter.objects.filter(owner=request.user).first()
    if shelter is None:
        messages.info(request, 'Спочатку створіть профіль притулку, щоб додавати тварин.')
        if request.method == 'POST':
            return JsonResponse({
                'success': False,
                'redirect_url': reverse('shelters:create_shelter'),
            }, status=409)
        return redirect('shelters:create_shelter')

    if not shelter.is_verified:
        message = 'Додавати тварин може лише притулок зі статусом «Перевірений».'
        if request.method == 'POST':
            return JsonResponse({'success': False, 'message': message}, status=403)
        raise PermissionDenied(message)

    if request.method == 'POST':
        form = AnimalForm(request.POST, request.FILES)
        if form.is_valid():
            animal = form.save(commit=False)
            animal.shelter = shelter
            animal.save()

            messages.success(request, 'Картку тварини створено.')

            return JsonResponse({
                'success': True,
                'redirect_url': reverse('animals:animal', args=[animal.pk]),
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors.get_json_data(),
            }, status=400)

    else:
        form = AnimalForm()

    return render(request, 'animals/animal_form.html', {
        'form': form,
        'title': 'Додати тварину',
        'form_description': 'Розкажіть про тварину та додайте її фото. Після збереження картка з’явиться на сайті.',
        'submit_label': 'Створити картку тварини',
        'form_action': reverse('animals:create_animal'),
        'app': 'animals',
    })

def edit_animal(request, animal_id):

    if not request.user.is_authenticated:
        messages.info(request, 'Увійдіть, щоб редагувати картку тварини.')
        if request.method == 'POST':
            return JsonResponse({
                'success': False,
                'redirect_url': reverse('accounts:login'),
            }, status=401)
        return redirect('accounts:login')

    if not request.user.is_shelter:
        message = 'Редагувати картку тварини може лише користувач із роллю «Притулок».'
        if request.method == 'POST':
            return JsonResponse({'success': False, 'message': message}, status=403)
        raise PermissionDenied(message)

    shelter = Shelter.objects.filter(owner=request.user).first()
    if shelter is None:
        messages.info(request, 'Спочатку створіть профіль притулку, щоб редагувати картку тварини.')
        if request.method == 'POST':
            return JsonResponse({
                'success': False,
                'redirect_url': reverse('shelters:create_shelter'),
            }, status=404)
        return redirect('shelters:create_shelter')

    if not shelter.is_verified:
        message = 'Редагувати картки тварин може лише перевірений притулок.'
        if request.method == 'POST':
            return JsonResponse({'success': False, 'message': message}, status=403)
        raise PermissionDenied(message)

    animal = get_object_or_404(Animal, pk=animal_id, shelter=shelter)
    if request.method == 'POST':
        form = AnimalForm(request.POST, request.FILES, instance=animal)

        if form.is_valid():
            if form.has_changed():
                form.save()
                messages.success(request, 'Зміни інформації про тварину збережено.')
            else:
                messages.info(request, 'Інформація про тварину залишилася без змін.')

            return JsonResponse({
                'success': True,
                'redirect_url': reverse('animals:manage_animals')
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors.get_json_data(),
            }, status=400)

    else:
        form = AnimalForm(instance=animal)

    return render(request, 'animals/animal_form.html', {
        'form': form,
        'title': 'Редагувати картку тварини',
        'form_description': 'Оновіть дані тварини або виберіть нове головне фото. Якщо фото не змінювати, збережеться поточне.',
        'submit_label': 'Зберегти зміни',
        'form_action': reverse('animals:edit_animal', args=[animal_id]),
        'app': 'animals',
    })

def manage_animals(request):

    if not request.user.is_authenticated:
        messages.info(request, 'Увійдіть, щоб переглянути тварин притулку.')
        return redirect('accounts:login')

    if not request.user.is_shelter:
        raise PermissionDenied('Ця сторінка доступна лише власникам притулків.')

    shelter = Shelter.objects.filter(owner=request.user).first()

    if shelter is None:
        messages.info(request, 'Спочатку створіть профіль притулку, щоб керувати тваринами.')
        return redirect('shelters:create_shelter')

    if not shelter.is_verified:
        raise PermissionDenied('Керувати тваринами може лише притулок зі статусом «Перевірений».')

    animals = Animal.objects.filter(shelter=shelter)

    return render(request, 'animals/animals_table.html', {
        'app': 'animals',
        'title': 'Тварини притулку',
        'animals': animals,
        'adoption_status_choices': Animal.Status.choices
    })
