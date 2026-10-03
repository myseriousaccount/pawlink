from django.shortcuts import render

from animals.models import Animal
from shelters.models import Shelter


def home(request):
    featured_animals = (
        Animal.objects.filter(
            shelter__status=Shelter.ShelterStatus.APPROVED,
            adoption_status=Animal.Status.AVAILABLE,
        )
        .select_related('shelter')
        .order_by('-pk')[:3]
    )

    return render(request, 'core/home.html',context={
        'title': 'Головна',
        'page': 'home',
        'app': 'core',
        'featured_animals': featured_animals,
    })

def about(request):
    return render(request, 'core/about.html',context={
        'title': 'Про нас',
        'page': 'about',
        'app': 'core'
    })


def contacts(request):
    return render(request, 'core/contacts.html',context={
        'title': 'Контакти',
        'page': 'contacts',
        'app': 'core'
    })
