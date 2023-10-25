from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
# Create your models here.

USER_TYPE_CHOICES = (
    ('student', 'Student'),
    ('teacher', 'Teacher'),
)
class CreateUserForm(UserCreationForm):
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, required=True, widget=forms.RadioSelect)
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']