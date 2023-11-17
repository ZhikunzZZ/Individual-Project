from django.db import models
from django.contrib.auth.models import User


class Channel(models.Model):
    name = models.CharField(max_length=70)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return self.name


class Section(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 评论者
    section = models.ForeignKey(Section, on_delete=models.CASCADE)  # 评论所属的section
    text = models.TextField(max_length=500)  # 评论内容

    def __str__(self):
        return f"Comment by {self.user.username} on {self.section.title}"
