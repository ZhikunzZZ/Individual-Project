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
from django.db.models import Q, Case, When, Value, IntegerField
from django.http import HttpResponseRedirect
from django.urls import reverse


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

def createSection(request, channel_id):
    channel = get_object_or_404(Channel, pk=channel_id)
    if request.method == 'POST':
        section_title = request.POST.get('channel-name')
        section_des = request.POST.get('channel-info')
        new_section = Section.objects.create(channel=channel, title=section_title, description=section_des)
        return redirect('section', channel_id=channel_id, section_id=new_section.id)
    user_info = UserInfo.objects.get(user=request.user)
    return render(request, 'create_section.html', {
        'username': user_info.profile_name,
        'user_image': user_info.user_image.url,
        'channel': channel
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

    search_query = request.GET.get('search', '')

    comments_query = Comment.objects.filter(section=current_section)
    if search_query:
        comments_query = comments_query.filter(text__icontains=search_query)

    # 总是注释 sort_read
    comments_query = comments_query.annotate(
        sort_read=Case(
            When(read=False, then=Value(1)),
            When(read=True, then=Value(0)),
            output_field=IntegerField(),
        )
    )

    sort = request.GET.get('sort', 'read')
    if sort == 'vote':
        comments = comments_query.order_by('-likes', '-sort_read')
    else:
        comments = comments_query.order_by('-sort_read', '-likes')

    user_info = UserInfo.objects.get(user=request.user)

    return render(request, 'section_detail.html', {
        'username': user_info.profile_name,
        'current_channel': current_channel,
        'sections': sections,
        'current_section': current_section,
        'channels': user_channels,
        'comments': comments,
        'user_image': user_info.user_image.url,
        'sort': sort,
        'search_query': search_query,
    })

def edit_section(request, channel_id, section_id):
    channel = get_object_or_404(Channel, pk=channel_id)
    section = get_object_or_404(Section, pk=section_id, channel=channel)
    if request.method == 'POST':
        section_title = request.POST.get('section_title')
        section_description = request.POST.get('section_description')

        if section_title:
            section.title = section_title
        if section_description:
            section.description = section_description
        section.save()
        return redirect('section', channel_id=channel_id, section_id=section_id)

    return render(request, 'edit_section_info.html', {
        'section': section,
        'channel': channel,
    })

def delete_section(request, section_id):
    section = get_object_or_404(Section, id=section_id, channel__user=request.user)
    channel_id = section.channel.id  # Capture the channel id to redirect after deletion
    section.delete()
    return HttpResponseRedirect(reverse('channel-detail', args=[channel_id]))

def mark_comment_as_read(request, comment_id):
    if request.method == "POST" and request.user.is_authenticated:
        comment = Comment.objects.get(id=comment_id)
        comment.read = True
        comment.save()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False})

def update_comment_reply(request, comment_id):
    if request.method == 'POST':
        comment = Comment.objects.get(id=comment_id)
        data = json.loads(request.body)
        comment.reply = data.get('reply')
        comment.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

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
