# Generated by Django 4.1.3 on 2022-12-21 11:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_bankaccount_is_verified'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bankaccount',
            name='is_verified',
        ),
    ]
