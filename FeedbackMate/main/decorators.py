from django.http import HttpResponse
from django.shortcuts import redirect

def unauthenticated_user(view_func):