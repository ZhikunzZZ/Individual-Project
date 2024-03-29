# Generated by Django 3.2.19 on 2024-01-31 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_auto_20240131_0556'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='five_star_percentage',
            field=models.FloatField(default=0.0, verbose_name='Percentage'),
        ),
        migrations.AddField(
            model_name='section',
            name='four_star_percentage',
            field=models.FloatField(default=0.0, verbose_name='Percentage'),
        ),
        migrations.AddField(
            model_name='section',
            name='one_star_percentage',
            field=models.FloatField(default=0.0, verbose_name='Percentage'),
        ),
        migrations.AddField(
            model_name='section',
            name='three_star_percentage',
            field=models.FloatField(default=0.0, verbose_name='Percentage'),
        ),
        migrations.AddField(
            model_name='section',
            name='two_star_percentage',
            field=models.FloatField(default=0.0, verbose_name='Percentage'),
        ),
    ]
