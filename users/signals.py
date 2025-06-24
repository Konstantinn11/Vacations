from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver
from .models import User_info, Unit
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User_info)
def update_superuser_status(instance, **kwargs):
    # Сохранение прав администратора у пользователя
    if instance.user.id == 1:
        return
    
    # Получаем отдел персонала
    hr_dept = Unit.objects.filter(title='Отдел персонала и безопасности (602)').first()
    
    if hr_dept:
        # Проверяем, находится ли пользователь в HR отделе
        is_hr = instance.otd_number == hr_dept
        
        # Обновляем статус суперпользователя
        if instance.user.is_superuser != is_hr:
            instance.user.is_superuser = is_hr
            instance.user.save()


@receiver(pre_save, sender=Unit)
def update_unit_boss_supervisor(sender, instance: Unit, **kwargs):
    """
    При изменении `Unit.boss` автоматически:
      1) снимает `supervisor` у предыдущего босса этого отдела,
      2) назначает новому боссу того же `supervisor`, что был у предыдущего босса.
    """
    # Обрабатываем только обновление существующего подразделения
    if instance._state.adding:
        return

    try:
        old_unit = Unit.objects.get(pk=instance.pk)
    except Unit.DoesNotExist:
        return

    old_boss = old_unit.boss
    new_boss = instance.boss

    if old_boss == new_boss:
        return

    supervisor_user = None
    if old_boss:
        old_info = User_info.objects.filter(user=old_boss).first()
        if old_info:
            supervisor_user = old_info.supervisor
            old_info.supervisor = None
            old_info.save()

    if new_boss and supervisor_user:
        new_info = User_info.objects.filter(user=new_boss).first()
        if new_info:
            new_info.supervisor = supervisor_user
            new_info.save()
