from django.shortcuts import render, HttpResponse
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
# Create your views here.
def index(request):
    return HttpResponse("hello!!!!!")

def login(request):
    return render(request, 'login.html')

def registerPage(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()

    context = {'form':form}
    return render(request, 'register.html', context)