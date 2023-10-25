from django.http import HttpResponse
from django.shortcuts import redirect
from django.http import HttpResponseForbidden

def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.groups.filter(name='student').exists():
                return redirect('student')
            elif request.user.groups.filter(name='teacher').exists():
                return redirect('teacher')
            else:
                return redirect('index')
        return view_func(request, *args, **kwargs)
    return wrapper_func

def student_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.groups.filter(name='student').exists():
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("You do not have permission to access this page.")
    return _wrapped_view

def teacher_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.groups.filter(name='teacher').exists():
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("You do not have permission to access this page.")
    return _wrapped_view