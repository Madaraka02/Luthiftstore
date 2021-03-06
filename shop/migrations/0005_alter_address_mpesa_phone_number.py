# Generated by Django 3.2.9 on 2021-11-28 21:02

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_alter_address_mpesa_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='mpesa_phone_number',
            field=models.CharField(max_length=16, null=True, validators=[django.core.validators.RegexValidator(message="do not add + to the phone number write it in this format: '999999999'. Up to 15 digits allowed.", regex='^\\1?\\d{9,15}$')]),
        ),
    ]
