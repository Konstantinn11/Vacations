from django.urls import path
from . import views

urlpatterns = [
    path('vacations/new/<int:year>/', views.vacation_new, name='vacation_new'),
    path('vacations/all/', views.vacations_start, name='vacations_start'),
    path('vacations/vacation_edit/<int:year>/<int:vac_id>/', views.vacation_edit, name='vacation_edit'),
    path('vacations/vacation_delete/<int:vac_id>/', views.vacation_delete, name='vacation_delete'),
    path('vacations/all/vac_by_us/<int:year>/<int:otd>/', views.vacations_by_user, name='vacations_by_user'),
    path('vacations/vacation_confirm/<int:year>/<int:otd>/<str:user>/<str:day>/', views.vacation_confirm_from_day, name='vacation_confirm_from_day'),
    path('vacations/del_vac_by_drop/<int:otd>/<str:user_name>/<str:day>/', views.del_vac_by_drop, name='del_vac_by_drop'),
    path('vacations/vac_2/<int:year>/<int:otd>/', views.vac_2, name='vac_2'),
    path('vacations/vac_2_days/<int:year>/<int:otd>/', views.vac_2_days, name='vac_2_days'),
    path('vac_all/<int:otd>/', views.vac_all, name='vac_all'),
    path('vac_calendars/<int:otd>/', views.vac_calendars, name='vac_calendars'),
    path('vac_my_vacations/', views.vac_my_vacations, name='vac_my_vacations'),
    path('vac_all_vacations/', views.vac_all_vacations, name='vac_all_vacations'),
    path('vacation/<int:vac_id>/', views.vacation_detail, name='vacation_detail'),
    path('import_vacations/', views.import_vacations, name='import_vacations'),
    path('vac_my_profile/', views.vac_my_profile, name='vac_my_profile'),
    path('profile_edit/', views.profile_edit, name='profile_edit'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('employees/', views.employees, name='employees'),
]