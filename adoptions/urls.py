from django.urls import path

from . import views

app_name = 'adoptions'
urlpatterns = [
    path('apply/<int:animal_id>/', views.application, name='application'),
    path('applications/manage/', views.manage_applications, name='manage_applications'),
    path('applications/<int:application_id>/review/', views.review_application, name='review_application'),
    path('applications/<int:application_id>/notes/', views.save_shelter_notes, name='save_shelter_notes'),
]
