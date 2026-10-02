from django.urls import path
from . import views

app_name = 'animals'
urlpatterns = [
    path('', views.animals_list, name='animals'),
    path('manage/', views.manage_animals, name='manage_animals'),
    path('<int:animal_id>/', views.animal_detail, name='animal'),
    path('favorite/<int:animal_id>/', views.add_to_favorite, name='favorite'),
    path('create/', views.create_animal, name='create_animal'),
    path('edit/<int:animal_id>/', views.edit_animal, name='edit_animal'),
    path('status/<int:animal_id>/', views.change_animal_status, name='change_animal_status'),
    path('updates/create/<int:animal_id>/', views.create_animal_update, name='create_animal_update'),
    path('images/create/<int:animal_id>/', views.add_animal_image, name='add_animal_image'),
]
