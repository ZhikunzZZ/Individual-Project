# Generated by Django 3.2.19 on 2023-11-17 04:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='channel',
            name='description',
            field=models.TextField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='section',
            name='description',
            field=models.TextField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='channel',
            name='name',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='section',
            name='title',
            field=models.CharField(max_length=20),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(max_length=100)),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.section')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]