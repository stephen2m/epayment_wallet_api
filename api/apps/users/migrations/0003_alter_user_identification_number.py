# Generated by Django 4.1.3 on 2022-12-21 11:23

from django.db import migrations
import encrypted_fields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_identification_number_user_identification_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='identification_number',
            field=encrypted_fields.fields.EncryptedCharField(max_length=15),
        ),
    ]
