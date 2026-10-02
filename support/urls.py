from django.urls import path
from . import views

app_name = 'support'
urlpatterns = [
    path('help/<int:need_id>/', views.contribution, name='contribution'),
    path('needs/create/<int:animal_id>/', views.create_need, name='create_need'),
    path('contributions/manage/', views.manage_contributions, name='manage_contributions'),
    path('contributions/manage/<int:contribution_id>/proof/', views.show_proof, name='show_proof'),
    path('contributions/<int:contribution_id>/review/', views.review_contribution, name='review_contribution'),
]
