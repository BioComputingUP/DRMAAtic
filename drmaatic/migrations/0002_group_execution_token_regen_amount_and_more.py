# Generated by Django 4.2.5 on 2023-09-29 09:08

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drmaatic', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='execution_token_regen_amount',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='group',
            name='execution_token_regen_time',
            field=models.CharField(default='30 seconds', max_length=40),
        ),
        migrations.AlterField(
            model_name='job',
            name='_status',
            field=models.CharField(choices=[('job has been rejected from the ws', 'Rejected'), ('job has been received from the ws', 'Received'), ('job has been created and sent to the DRM', 'Created'), ('process status cannot be determined', 'Undetermined'), ('job is queued and active', 'Queued Active'), ('job is queued and in system hold', 'System On Hold'), ('job is queued and in user hold', 'User On Hold'), ('job is queued and in user and system hold', 'User System On Hold'), ('job is running', 'Running'), ('job is system suspended', 'System Suspended'), ('job is user suspended', 'User Suspended'), ('job was stopped by the user', 'Stopped'), ('job finished normally', 'Done'), ('job finished, but failed', 'Failed')], default='job has been received from the ws', max_length=200),
        ),
        migrations.AlterField(
            model_name='task',
            name='required_tokens',
            field=models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
