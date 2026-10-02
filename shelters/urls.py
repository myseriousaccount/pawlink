from django.urls import path
from . import views

app_name = 'shelters'
urlpatterns = [
    path('create/', views.create_shelter, name='create_shelter'),
    path('edit/', views.edit_shelter, name='edit_shelter'),
]
