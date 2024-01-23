"""
URL configuration for FeedbackMate project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from main import views


urlpatterns = [
    path('admin', admin.site.urls),
    path('index/', views.index, name="index"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerPage, name="register"),
    path('student/', views.studentPage, name="student"),
    path('teacher/', views.teacherPage, name="teacher"),
    path('edit-personal-info/', views.editPersonalInfoPage, name="personal-info"),
    path('teacher/channel/<int:channel_id>/', views.channel, name='channel-detail'),
    path('teacher/channel/<int:channel_id>/section/<int:section_id>/', views.section, name='section'),
    path('teacher/create_channel/', views.createChannel, name="create-channel"),
    path('delete-channel/<int:channel_id>/', views.delete_channel, name='delete-channel'),
    path('mark-comment-as-read/<int:comment_id>/', views.mark_comment_as_read, name='mark-comment-as-read'),
    path('update-comment-reply/<int:comment_id>/', views.update_comment_reply, name='update-comment-reply'),
    path('your-endpoint', views.sort_comments, name='sort_comments'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

