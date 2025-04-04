from django.urls import path
from . import views
from .views import CustomPasswordResetView, CustomPasswordResetDoneView

urlpatterns = [
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('vac_all/<int:otd>/', views.vac_all, name='vac_all'),
    path('vac_calendars/<int:otd>/', views.vac_calendars, name='vac_calendars'),
    path('vacations/vac_2/<int:year>/<int:otd>/', views.vac_2, name='vac_2'),
    path('vacations/vac_2_days/<int:year>/<int:otd>/', views.vac_2_days, name='vac_2_days'),
    path('vacations/new/<int:year>/', views.vacation_new, name='vacation_new'),
    path('vacations/vacation_edit/<int:year>/<int:vac_id>/', views.vacation_edit, name='vacation_edit'),
    path('vacations/vacation_delete/<int:vac_id>/', views.vacation_delete, name='vacation_delete'),
    path('vacation/<int:vac_id>/', views.vacation_detail, name='vacation_detail'),
    path('vac_all_vacations/', views.vac_all_vacations, name='vac_all_vacations'),
    path('vac_my_vacations/', views.vac_my_vacations, name='vac_my_vacations'),
    path('import_vacations/', views.import_vacations, name='import_vacations'),
    path('vac_my_profile/', views.vac_my_profile, name='vac_my_profile'),
    path('profile_edit/', views.profile_edit, name='profile_edit'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('employees/', views.employees, name='employees'),
]