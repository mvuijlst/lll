from django.urls import path
from . import views

app_name = 'academies'

urlpatterns = [
    path('', views.academy_list, name='academy_list'),
    path('academy/<int:pk>/', views.academy_detail, name='academy_detail'),
    path('academy/<int:pk>/upload-logo/', views.academy_logo_upload, name='academy_logo_upload'),
    path('offerings/', views.offering_list, name='offering_list'),
    path('offering/<int:pk>/', views.offering_detail, name='offering_detail'),
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teacher/<int:pk>/', views.teacher_detail, name='teacher_detail'),
    path('search/', views.search_results, name='search_results'),
]
