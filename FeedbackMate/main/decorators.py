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
        return view_func(request, *args, **kwargs)
    return wrapper_func


def student_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.groups.filter(name='student').exists():
            return view_func(request, *args, **kwargs)
        else:
            return redirect('teacher')
    return _wrapped_view


def teacher_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.groups.filter(name='teacher').exists():
            return view_func(request, *args, **kwargs)
        else:
            return redirect('student')
    return _wrapped_view
