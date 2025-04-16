from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    patronymic = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name="Отчество"
        )
    groups = models.ManyToManyField(
        'auth.Group', 
        related_name='customuser_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', 
        related_name='customuser_set',
        blank=True
    )

class Unit(models.Model):
    title = models.CharField(
        max_length=200, 
        verbose_name='Номер отдела'
    )
    description = models.CharField(
        blank=True, 
        null=True, 
        max_length=200, 
        verbose_name='Название отдела'
    )
    boss = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_units',
        verbose_name='Руководитель отдела'
    )

    class Meta:
        ordering = ('title',)
        verbose_name = 'Отдел'
        verbose_name_plural = 'Отделы'

    def __str__(self) -> str:
        return self.title
    

class Tag(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название тега'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name
    

class User_info(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='user_info',
        verbose_name='Пользователь'
    )
    position = models.ForeignKey(
        'Position',
        on_delete=models.CASCADE,
        related_name='position_info',
        null=True,
        blank=True,
        verbose_name='Должность'
    )
    supervisor = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinate_leaders',
        verbose_name='Вышестоящий руководитель'
    )
    otd_number = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Номер отдела'
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        verbose_name='Теги',
        related_name='tags_info'
    )
    phone_number = models.TextField(
        blank=True,
        null=True,
        verbose_name='Номер телефона'
    )
    vacs_archiv = models.BooleanField(
        null=True,
        blank=True,
        default=False,
        verbose_name='Архивирован'
    )

    class Meta:
        ordering = ('user', )
        verbose_name = 'Информация о пользователе'
        verbose_name_plural = 'Информация о пользователях'


class Position(models.Model):
    position = models.CharField(
        max_length=200, 
        verbose_name='Должность'
    )

    class Meta:
        ordering = ('position',)
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'

    def __str__(self) -> str:
        return self.position


class Vacation(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='user_vacations',
        blank=True,
        null=True,
        verbose_name='Пользователь'
    )
    day_start = models.DateField(
        blank=True,
        null=True,
        verbose_name='Дата начала'
    )
    day_end = models.DateField(
        blank=True,
        null=True,
        verbose_name='Дата окончания'
    )
    how_long = models.TextField(
        blank=True,
        null=True,
        verbose_name='Всего дней'
    )
    year = models.TextField(
        blank=True,
        null=True,
        verbose_name='Период'
    )
    can_redact = models.BooleanField(
        blank=True,
        null=True,
        default=True,
        verbose_name='Возможность редактировать'
    )

    class Meta:
        ordering = ('user', 'day_start', )
        verbose_name = 'Отпуск'

    def save(self, *args, **kwargs):
        self.year = str(self.day_start.year)
        super().save(*args, **kwargs)
