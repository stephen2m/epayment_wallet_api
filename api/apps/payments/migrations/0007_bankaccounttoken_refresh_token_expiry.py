# Generated by Django 4.1.3 on 2022-12-22 09:44

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0006_remove_paymentrequest_beneficiary_account_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bankaccounttoken',
            name='refresh_token_expiry',
            field=models.DateTimeField(default=datetime.datetime(2023, 12, 22, 9, 44, 21, 575281, tzinfo=datetime.timezone.utc)),
            preserve_default=False,
        ),
    ]