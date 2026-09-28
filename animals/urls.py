from django.urls import path
from . import views

app_name = 'animals'
urlpatterns = [
    path('', views.animals_list, name='animals'),
    path('<int:animal_id>/', views.animal_detail, name='animal'),
    path('favorite/<int:animal_id>/', views.add_to_favorite, name='favorite'),
]