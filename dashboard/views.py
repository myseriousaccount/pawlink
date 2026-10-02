from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied

from adoptions.models import AdoptionApplication
from animals.models import Animal
from shelters.models import Shelter
from support.models import SupportContribution


# Create your views here.
def shelter_dashboard(request):

    if not request.user.is_authenticated:
        messages.info(request, 'Увійдіть, щоб відкрити панель притулку.')
        return redirect('accounts:login')

    if not request.user.is_shelter:
        raise PermissionDenied('Панель притулку доступна лише власникам притулків.')

    shelter = Shelter.objects.filter(owner=request.user).first()
    if shelter is None:
        messages.info(request, 'Спочатку створіть профіль притулку, щоб відкрити панель.')
        return redirect('shelters:create_shelter')

    animals_count = Animal.objects.filter(shelter=shelter).count()
    adoption_application_count = AdoptionApplication.objects.filter(
        animal__shelter=shelter,
        status=AdoptionApplication.ApplicationStatus.PENDING,
    ).count()
    pending_contributions_count = SupportContribution.objects.filter(
        need__animal__shelter=shelter,
        status=SupportContribution.ContributionStatus.PENDING,
    ).count()

    return render(request, 'dashboards/shelter.html', context={
        'title': 'Панель притулку',
        'page': 'shelter dashboard',
        'app': 'dashboard',
        'shelter': shelter,
        'animals_count': animals_count,
        'adoption_application_count': adoption_application_count,
        'pending_contributions_count': pending_contributions_count,
    })
