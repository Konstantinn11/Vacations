# Generated by Django 4.2.19 on 2025-03-24 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_position_position'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vacation',
            name='day_end',
            field=models.DateField(blank=True, null=True, verbose_name='Дата окончания'),
        ),
        migrations.AlterField(
            model_name='vacation',
            name='day_start',
            field=models.DateField(blank=True, null=True, verbose_name='Дата начала'),
        ),
    ]
