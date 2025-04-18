# Generated by Django 4.2.5 on 2023-11-22 10:27

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drmaatic', '0008_alter_task_queue_alter_user_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='queue',
            name='max_cpu',
            field=models.PositiveIntegerField(default=16, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(64)], verbose_name='Maximum CPUs per node'),
        ),
        migrations.AlterField(
            model_name='queue',
            name='max_mem',
            field=models.PositiveIntegerField(default=1024, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(96000)], verbose_name='Maximum memory (MB) per node'),
        ),
    ]
