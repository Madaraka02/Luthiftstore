# Generated by Django 3.2.9 on 2021-11-30 08:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0009_alter_address_mpesa_phone_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='phone_number',
        ),
    ]