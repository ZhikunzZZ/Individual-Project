# Generated by Django 3.2.19 on 2024-01-31 01:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_channel_pin_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channel',
            name='pin_code',
            field=models.CharField(blank=True, max_length=6, null=True, unique=True),
        ),
    ]
