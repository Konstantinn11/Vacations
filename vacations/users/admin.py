from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, User_info

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': ('last_name', 'first_name', 'patronymic', 'email')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Даты', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {'fields': ('username', 'password1', 'password2')}),
        ('Персональная информация', {'fields': ('last_name', 'first_name', 'patronymic', 'email')}),
    )

    list_display = ('username', 'last_name', 'first_name', 'patronymic', 'email')
    
    search_fields = ('username', 'first_name', 'last_name', 'email')

admin.site.register(CustomUser, CustomUserAdmin)

class User_infoAdmin(admin.ModelAdmin):
    """Информация о пользователях"""
    list_display = (
        'user', 'boss', 'otd_number',
        'vacs_access', 'vacs_archiv'
    )
    search_fields = ('username', )


admin.site.register(User_info, User_infoAdmin)
