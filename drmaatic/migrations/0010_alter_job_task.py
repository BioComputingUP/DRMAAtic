# Generated by Django 4.2.5 on 2023-12-14 14:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drmaatic', '0009_alter_queue_max_cpu_alter_queue_max_mem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='drmaatic.task'),
        ),
    ]
