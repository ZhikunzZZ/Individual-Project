from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .decorators import unauthenticated_user, teacher_required,student_required
# Create your views here.
@login_required(login_url='login')
def index(request):
    return render(request, 'main.html')

@login_required(login_url='login')
@teacher_required
def teacherPage(request):
    return HttpResponse("This is teacher page.")

@login_required(login_url='login')
@student_required
def studentPage(request):
    return HttpResponse("This is student page.")

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
            messages.info(request, 'Username or password incorrect')
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
            user_type = form.cleaned_data.get('user_type')

            if user_type == 'student':
                group, created = Group.objects.get_or_create(name='student')
                user.groups.add(group)
            elif user_type == 'teacher':
                group, created = Group.objects.get_or_create(name='teacher')
                user.groups.add(group)

            messages.success(request, 'Account was created for' + username)
            return redirect('login')

    context = {'form':form}
    return render(request, 'register.html', context)