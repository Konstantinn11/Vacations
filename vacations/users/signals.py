from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User_info, Unit

@receiver(post_save, sender=User_info)
def update_superuser_status(instance, **kwargs):
    # Получаем отдел персонала
    hr_dept = Unit.objects.filter(title='Отдел персонала и безопасности (602)').first()
    
    if hr_dept:
        # Проверяем, находится ли пользователь в HR отделе
        is_hr = instance.otd_number == hr_dept
        
        # Обновляем статус суперпользователя
        if instance.user.is_superuser != is_hr:
            instance.user.is_superuser = is_hr
            instance.user.save()