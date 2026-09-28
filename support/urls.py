from django.urls import path
from . import views

app_name = 'support'
urlpatterns = [
    path('help/<int:need_id>/', views.contribution, name='contribution'),
]