# Generated by Django 3.2.19 on 2024-01-31 05:56

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0016_comment_is_anonymous'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='five_star_users',
            field=models.ManyToManyField(blank=True, related_name='five_star_sections', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='section',
            name='four_star_users',
            field=models.ManyToManyField(blank=True, related_name='four_star_sections', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='section',
            name='one_star_users',
            field=models.ManyToManyField(blank=True, related_name='one_star_sections', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='section',
            name='ratings_count',
            field=models.PositiveIntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='section',
            name='three_star_users',
            field=models.ManyToManyField(blank=True, related_name='three_star_sections', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='section',
            name='total_rating',
            field=models.FloatField(blank=True, default=0.0),
        ),
        migrations.AddField(
            model_name='section',
            name='two_star_users',
            field=models.ManyToManyField(blank=True, related_name='two_star_sections', to=settings.AUTH_USER_MODEL),
        ),
    ]
