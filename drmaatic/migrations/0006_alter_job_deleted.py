# Generated by Django 4.2.5 on 2023-10-03 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drmaatic', '0005_alter_user_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
    ]