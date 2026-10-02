from django.urls import path
from . import views

app_name = 'dashboard'
urlpatterns = [
    path('shelter/', views.shelter_dashboard, name='shelter_dashboard'),
]