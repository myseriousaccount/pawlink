from django.urls import path
from . import views

app_name = 'shelters'
urlpatterns = [
    path('', views.shelters_list, name='shelters'),

]