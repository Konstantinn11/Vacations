from django.urls import path
from . import views
from .views import CustomPasswordResetView, CustomPasswordResetDoneView, get_department_employees

urlpatterns = [
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('vac_all/<int:otd>/', views.vac_all, name='vac_all'),
    path('vac_calendars/<int:otd>/', views.vac_calendars, name='vac_calendars'),
    path('vacations/vac_2/<int:year>/<int:otd>/', views.vac_2, name='vac_2'),
    path('vacations/new/<int:year>/', views.vacation_new, name='vacation_new'),
    path('vacations/vacation_edit/<int:year>/<int:vac_id>/', views.vacation_edit, name='vacation_edit'),
    path('vacations/vacation_delete/<int:vac_id>/', views.vacation_delete, name='vacation_delete'),
    path('vacation/<int:vac_id>/', views.vacation_detail, name='vacation_detail'),
    path('vac_all_vacations/', views.vac_all_vacations, name='vac_all_vacations'),
    path('vac_my_vacations/', views.vac_my_vacations, name='vac_my_vacations'),
    path('import_vacations/', views.import_vacations, name='import_vacations'),
    path('profile/<int:user_id>/', views.profile_view, name='profile'),
    path('profile/<int:user_id>/edit/', views.profile_edit, name='profile_edit'),
    path('employees/', views.employees, name='employees'),
    path('ajax/get_department_employees/', get_department_employees, name='get_department_employees'),
    path('vacations/export/<int:year>/<int:otd>/', views.export_vacations, name='export_vacations'),
    path('save-vacations/', views.save_vacations, name='save_vacations'),
    path('tags/add/', views.tag_create, name='tag_create'),
    path('tags/<int:pk>/edit/', views.tag_update, name='tag_update'),
    path('tags/<int:pk>/delete/', views.tag_delete, name='tag_delete'),
    path('units/add/', views.unit_create, name='unit_create'),
    path('units/<int:pk>/edit/', views.unit_update, name='unit_update'),
    path('units/<int:pk>/delete/', views.unit_delete, name='unit_delete'),
    path('employees/create/', views.employee_create, name='employee_create'),
    path('employees/manager/create/', views.manager_create, name='manager_create'),
    path('employees/manager/edit/<int:supervisor_id>/', views.manager_edit, name='manager_edit'),
    path('managers/<int:pk>/delete/', views.manager_delete, name='manager_delete'),
]