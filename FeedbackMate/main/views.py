import json
from django.http import JsonResponse
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .decorators import unauthenticated_user, teacher_required, student_required
from .models import Channel, Section, Comment, UserInfo
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404


# Create your views here.
@login_required(login_url='login')
def index(request):
    return render(request, 'main.html')


@login_required(login_url='login')
@teacher_required
def teacherPage(request):
    # 查询当前用户关联的 Channel
    user_channels = Channel.objects.filter(user=request.user)
    user_info = UserInfo.objects.get(user=request.user)
    # 将 channels 作为上下文传递给模板
    return render(request, 'teacher.html', {
        'username': user_info.profile_name,
        'channels': user_channels,
        'user_image':  user_info.user_image.url,
    })

# def teacherSectionPage(request, channel_id):

@login_required(login_url='login')
@student_required
def studentPage(request):
    user_info = UserInfo.objects.get(user=request.user)
    return render(request, 'student.html', {'username': user_info.profile_name})


def editPersonalInfoPage(request):
    if request.method == 'POST':
        profile_name = request.POST.get('profile_name')
        user_image = request.FILES.get('user_image')

        user_info = UserInfo.objects.get(user=request.user)
        if profile_name:
            user_info.profile_name = profile_name
        if user_image:
            user_info.user_image = user_image
        user_info.save()
        return redirect('teacher')

    user_info = UserInfo.objects.get(user=request.user)
    return render(request, 'edit_user_info.html', {
        'user_info': user_info,
        'username': user_info.profile_name,
        'user_image': user_info.user_image.url
    })

def channel(request, channel_id):
    user_channels = Channel.objects.filter(user=request.user)
    current_channel = Channel.objects.get(id=channel_id)
    sections = Section.objects.filter(channel=current_channel)
    user_info = UserInfo.objects.get(user=request.user)
    # Render a new template while keeping the layout consistent with 'teacher.html'
    return render(request, 'channel_detail.html', {
        'username': user_info.profile_name,
        'current_channel': current_channel,
        'sections': sections,
        'channels': user_channels,
        'user_image': user_info.user_image.url,
    })


def createChannel(request):
    if request.method == 'POST':
        channel_name = request.POST.get('channel-name')
        channel_info = request.POST.get('channel-info')
        channel_image = request.FILES.get('channel-image')
        if channel_image is not None:
            Channel.objects.create(name=channel_name, description=channel_info, user=request.user, image=channel_image)
            return redirect('teacher')
        else:
            Channel.objects.create(name=channel_name, description=channel_info, user=request.user)
            return redirect('teacher')
    user_info = UserInfo.objects.get(user=request.user)
    return render(request, 'create_channel.html', {
        'username': user_info.profile_name,
        'user_image': user_info.user_image.url,
    })


@require_POST
def delete_channel(request, channel_id):
    try:
        channel = Channel.objects.get(id=channel_id)
        channel.delete()
        return JsonResponse({'success': True})
    except Channel.DoesNotExist:
        return JsonResponse({'error': 'Channel not found'}, status=404)
    except Exception as e:
        # 在开发阶段，打印错误信息可以帮助诊断问题
        print(str(e))
        return JsonResponse({'error': 'Internal Server Error'}, status=500)

def section(request, channel_id, section_id):
    user_channels = Channel.objects.filter(user=request.user)
    current_channel = Channel.objects.get(id=channel_id)
    sections = Section.objects.filter(channel=current_channel)
    current_section = Section.objects.get(id=section_id)
    comments = Comment.objects.filter(section=current_section)
    user_info = UserInfo.objects.get(user=request.user)
    # Render a new template while keeping the layout consistent with 'teacher.html'
    return render(request, 'section_detail.html', {
        'username': user_info.profile_name,
        'current_channel': current_channel,
        'sections': sections,
        'current_section': current_section,
        'channels': user_channels,
        'comments': comments,
        'user_image': user_info.user_image.url,
    })


@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.groups.filter(name='student').exists():
                return redirect('student')
            elif user.groups.filter(name='teacher').exists():
                return redirect('teacher')
            else:
                return redirect('index')
        else:
            messages.error(request, 'Username or password incorrect')
    return render(request, 'login.html')


def logoutUser(request):
    logout(request)
    return redirect('login')


@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            user_type = request.POST.get('user_type')
            UserInfo.objects.create(user=user, profile_name='User')

            if user_type == 'student':
                group, created = Group.objects.get_or_create(name='student')
                user.groups.add(group)
            elif user_type == 'teacher':
                group, created = Group.objects.get_or_create(name='teacher')
                user.groups.add(group)

            messages.success(request, 'Account was created for' + username)
            return redirect('login')

    context = {'form': form}
    return render(request, 'register.html', context)
