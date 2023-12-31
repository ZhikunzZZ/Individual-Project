# Generated by Django 3.2.19 on 2023-11-17 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20231117_0426'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channel',
            name='description',
            field=models.TextField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='channel',
            name='name',
            field=models.CharField(max_length=70),
        ),
        migrations.AlterField(
            model_name='comment',
            name='text',
            field=models.TextField(max_length=500),
        ),
        migrations.AlterField(
            model_name='section',
            name='description',
            field=models.TextField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='section',
            name='title',
            field=models.CharField(max_length=50),
        ),
    ]
