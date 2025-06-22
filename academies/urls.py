from django.urls import path
from . import views

app_name = 'academies'

urlpatterns = [
    path('', views.academy_list, name='academy_list'),
    path('academy/<int:pk>/', views.academy_detail, name='academy_detail'),
    path('offerings/', views.offering_list, name='offering_list'),
]
