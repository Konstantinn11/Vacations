from django.urls import path
from . import views

app_name = 'holiday_calendar'

urlpatterns = [
    path('', views.holiday_list, name='holiday_list'),
    path('add/', views.holiday_edit, name='holiday_add'),
    path('edit/<int:pk>/', views.holiday_edit, name='holiday_edit'),
    path('delete/<int:pk>/', views.holiday_delete, name='holiday_delete'),
]