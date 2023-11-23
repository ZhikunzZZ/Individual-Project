from django.contrib import admin
from .models import Channel, Section, Comment, UserInfo

# Register your models here.

admin.site.register(Channel)
admin.site.register(Section)
admin.site.register(Comment)
admin.site.register(UserInfo)
