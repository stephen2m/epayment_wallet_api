# Generated by Django 4.1.3 on 2022-12-28 13:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0010_alter_paymentrequest_stitch_ref'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='paymentrequest',
            options={'ordering': ['-created']},
        ),
    ]
