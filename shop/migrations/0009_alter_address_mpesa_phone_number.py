# Generated by Django 3.2.9 on 2021-11-30 08:36

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0008_alter_address_mpesa_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='mpesa_phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=128, null=True, region=None),
        ),
    ]
