from django.urls import path
from . import views

app_name = 'adoptions'
urlpatterns = [
    path('apply/<int:animal_id>/', views.application, name='application'),
]