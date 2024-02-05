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
from django.db.models import Q, Case, When, Value, IntegerField, F
from django.http import HttpResponseRedirect
from django.urls import reverse
from collections import defaultdict
import re
import random
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import pos_tag


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
    user_channels = request.user.joined_channels.all()
    user_info = UserInfo.objects.get(user=request.user)
    return render(request, 'student.html', {
        'username': user_info.profile_name,
        'channels': user_channels,
        'user_image': user_info.user_image.url,
    })


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

def studentChannel(request, channel_id):
    user_channels = request.user.joined_channels.all()
    current_channel = Channel.objects.get(id=channel_id)
    sections = Section.objects.filter(channel=current_channel)
    user_info = UserInfo.objects.get(user=request.user)
    return render(request, 'student_channel_detail.html', {
        'username': user_info.profile_name,
        'current_channel': current_channel,
        'sections': sections,
        'channels': user_channels,
        'user_image': user_info.user_image.url,
    })


def joinChannel(request):
    user_info = UserInfo.objects.get(user=request.user)
    if request.method == 'POST':
        pin_code = ''.join(request.POST.getlist('pin_code[]'))
        try:
            channel = Channel.objects.get(pin_code=pin_code)
            if request.user in channel.students.all():
                messages.info(request, 'You have already joined this channel.')
            else:
                channel.students.add(request.user)
                return redirect('student-channel-detail', channel_id=channel.id)
        except Channel.DoesNotExist:
            messages.error(request, 'Invalid PIN code. Please try again.')
    return render(request, 'join_channel.html', {
        'pin_code': range(6),
        'user_image': user_info.user_image.url,
    })

def generate_pin_code():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))

# 创建唯一 PIN 码的函数
def create_unique_pin_code():
    while True:
        pin_code = generate_pin_code()
        if not Channel.objects.filter(pin_code=pin_code).exists():
            return pin_code



def createChannel(request):
    if request.method == 'POST':
        channel_name = request.POST.get('channel-name')
        channel_info = request.POST.get('channel-info')
        channel_image = request.FILES.get('channel-image')
        pin_code = create_unique_pin_code()
        if channel_image is not None:
            Channel.objects.create(name=channel_name, description=channel_info, user=request.user, image=channel_image, pin_code=pin_code)
            return redirect('teacher')
        else:
            Channel.objects.create(name=channel_name, description=channel_info, user=request.user, pin_code=pin_code)
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

    comments = Comment.objects.filter(section=current_section)
    common_words = set(stopwords.words('english'))
    keyword_freq = defaultdict(int)

    for comment in comments:
        text = comment.text.lower()
        likes = comment.likes
        text = re.sub(r'[^\w\s]', '', text)
        words = word_tokenize(text)
        tagged_words = pos_tag(words)

        for word, tag in tagged_words:
            if word not in common_words and (tag == 'NN' or tag == 'JJ'):
                keyword_freq[word] += likes

    sorted_keywords = sorted(keyword_freq.items(), key=lambda item: item[1], reverse=True)
    top_keywords = sorted_keywords[:10]

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
        'top_keywords': top_keywords,
    })


def studentSection(request, channel_id, section_id):
    user_channels = request.user.joined_channels.all()
    current_channel = Channel.objects.get(id=channel_id)
    sections = Section.objects.filter(channel=current_channel)
    current_section = Section.objects.get(id=section_id)

    search_query = request.GET.get('search', '')
    comments_query = Comment.objects.filter(section=current_section)
    if search_query:
        comments_query = comments_query.filter(text__icontains=search_query)

    # 总是注释 sort_read
    sort = request.GET.get('sort', 'user_first')
    comments_query = comments_query.annotate(
        current_user_comment=Case(
            When(user=request.user, then=Value(1)),
            default=Value(0),
            output_field=IntegerField()
        )
    )
    if sort == 'user_first':
        comments = comments_query.order_by('-current_user_comment', '-likes')
    else:
        comments = comments_query.order_by('-likes', '-current_user_comment')

    user_info = UserInfo.objects.get(user=request.user)



    user_rating = 0
    if current_section.one_star_users.filter(id=request.user.id).exists():
        user_rating = 1
    elif current_section.two_star_users.filter(id=request.user.id).exists():
        user_rating = 2
    elif current_section.three_star_users.filter(id=request.user.id).exists():
        user_rating = 3
    elif current_section.four_star_users.filter(id=request.user.id).exists():
        user_rating = 4
    elif current_section.five_star_users.filter(id=request.user.id).exists():
        user_rating = 5

    return render(request, 'student_section_detail.html', {
        'username': user_info.profile_name,
        'current_channel': current_channel,
        'sections': sections,
        'current_section': current_section,
        'channels': user_channels,
        'comments': comments,
        'user_image': user_info.user_image.url,
        'sort': sort,
        'search_query': search_query,
        'user_rating': user_rating,
    })


def toggle_like(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        comment_id = data['comment_id']
        comment = Comment.objects.get(id=comment_id)
        user = request.user

        if user in comment.liked_users.all():
            comment.liked_users.remove(user)
            liked = False
        else:
            comment.liked_users.add(user)
            liked = True

        comment.likes = comment.liked_users.count()
        comment.save()

        return JsonResponse({'liked': liked, 'likes': comment.likes})

    return JsonResponse({'error': 'Invalid request'}, status=400)


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

def exit_channel(request, channel_id):
    channel = get_object_or_404(Channel, id=channel_id)
    if request.user in channel.students.all():
        # 如果是成员，则将其从频道中移除
        channel.students.remove(request.user)
    return redirect('student')


def submit_feedback(request, section_id):
    section = get_object_or_404(Section, id=section_id)
    if request.method == 'POST':
        text = request.POST.get('feedback_content')
        is_anonymous = 'anonymous' in request.POST

        Comment.objects.create(
            user=request.user,
            section=section,
            text=text,
            is_anonymous=is_anonymous
        )

        # 重定向到合适的页面
        return redirect('student-section', channel_id=section.channel.id, section_id=section_id)

    # 如果不是 POST 请求，则重定向或显示错误
    return redirect('student-section', channel_id=section.channel.id, section_id=section_id)


def rate_section(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        section_id = data['section_id']
        rating = int(data['rating'])
        user = request.user  # 获取当前登录的用户

        section = Section.objects.get(id=section_id)

        # 从所有评分列表中移除用户
        section.one_star_users.remove(user)
        section.two_star_users.remove(user)
        section.three_star_users.remove(user)
        section.four_star_users.remove(user)
        section.five_star_users.remove(user)

        # 根据评分将用户添加到相应列表
        if rating == 1:
            section.one_star_users.add(user)
        elif rating == 2:
            section.two_star_users.add(user)
        elif rating == 3:
            section.three_star_users.add(user)
        elif rating == 4:
            section.four_star_users.add(user)
        elif rating == 5:
            section.five_star_users.add(user)

        # 重新计算各星级用户的数量和百分比
        total_users = section.one_star_users.count() + section.two_star_users.count() + \
                      section.three_star_users.count() + section.four_star_users.count() + \
                      section.five_star_users.count()

        section.ratings_count = total_users
        section.total_rating = round(sum([2 * section.one_star_users.count(),
                                    4 * section.two_star_users.count(),
                                    6 * section.three_star_users.count(),
                                    8 * section.four_star_users.count(),
                                    10 * section.five_star_users.count()]) / total_users if total_users > 0 else 0, 1)

        section.one_star_percentage = round(
            (section.one_star_users.count() / total_users * 100) if total_users > 0 else 0, 1)
        section.two_star_percentage = round(
            (section.two_star_users.count() / total_users * 100) if total_users > 0 else 0, 1)
        section.three_star_percentage = round(
            (section.three_star_users.count() / total_users * 100) if total_users > 0 else 0, 1)
        section.four_star_percentage = round(
            (section.four_star_users.count() / total_users * 100) if total_users > 0 else 0, 1)
        section.five_star_percentage = round(
            (section.five_star_users.count() / total_users * 100) if total_users > 0 else 0, 1)

        section.save()
        # 返回更新后的数据
        return JsonResponse({
            'total_rating': f"{section.total_rating:.1f}",
            'ratings_count': section.ratings_count,
            '1_star_percentage': f"{section.one_star_percentage:.1f}",
            '2_star_percentage': f"{section.two_star_percentage:.1f}",
            '3_star_percentage': f"{section.three_star_percentage:.1f}",
            '4_star_percentage': f"{section.four_star_percentage:.1f}",
            '5_star_percentage': f"{section.five_star_percentage:.1f}",

        })


def delete_comment(request, comment_id):
    if request.method == 'POST':
        comment = get_object_or_404(Comment, pk=comment_id, user=request.user)  # Ensures the user can only delete their own comments
        comment.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)


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
