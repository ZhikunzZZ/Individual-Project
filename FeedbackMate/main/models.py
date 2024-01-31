from django.db import models
from django.contrib.auth.models import User
import os
from uuid import uuid4

# Function to generate a unique path for each uploaded image



def channel_image_path(instance, filename):
    # Get file extension
    ext = filename.split('.')[-1]
    # Generate a unique filename using UUID
    filename = f'{uuid4()}.{ext}'
    # Return the complete file path
    return os.path.join('channel_images', str(instance.user.id), filename)


def user_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid4()}.{ext}'
    return os.path.join('user_images', str(instance.user.id), filename)


class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_name = models.CharField(max_length=30)
    user_image = models.ImageField(upload_to=user_image_path, default='img/user.png')

    def __str__(self):
        return self.profile_name


class Channel(models.Model):
    name = models.CharField(max_length=70)
    pin_code = models.CharField(max_length=6, unique=True, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(max_length=500, blank=True)
    image = models.ImageField(upload_to=channel_image_path, default='img/channel_icon.jpg')
    students = models.ManyToManyField(User, related_name='joined_channels', blank=True)
    def __str__(self):
        return self.name


class Section(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=500, blank=True)
    total_rating = models.FloatField(default=0.0, blank=True)
    ratings_count = models.PositiveIntegerField(default=0, blank=True)
    one_star_users = models.ManyToManyField(User, related_name='one_star_sections', blank=True)
    two_star_users = models.ManyToManyField(User, related_name='two_star_sections', blank=True)
    three_star_users = models.ManyToManyField(User, related_name='three_star_sections', blank=True)
    four_star_users = models.ManyToManyField(User, related_name='four_star_sections', blank=True)
    five_star_users = models.ManyToManyField(User, related_name='five_star_sections', blank=True)
    one_star_percentage = models.FloatField(verbose_name="Percentage", default=0.0)
    two_star_percentage = models.FloatField(verbose_name="Percentage", default=0.0)
    three_star_percentage = models.FloatField(verbose_name="Percentage", default=0.0)
    four_star_percentage = models.FloatField(verbose_name="Percentage", default=0.0)
    five_star_percentage = models.FloatField(verbose_name="Percentage", default=0.0)

    def __str__(self):
        return self.title


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 评论者
    section = models.ForeignKey(Section, on_delete=models.CASCADE)  # 评论所属的section
    text = models.TextField(max_length=500)  # 评论内容
    read = models.BooleanField(default=False)
    reply = models.TextField(blank=True, null=True)
    is_anonymous = models.BooleanField(default=False)
    liked_users = models.ManyToManyField(User, related_name='liked_comments', blank=True)
    likes = models.IntegerField(default=0)

    def __str__(self):
        return self.text


