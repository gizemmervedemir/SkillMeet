from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'bio', 'skills_can_teach', 'skills_want_to_learn', 'city')

class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('bio', 'skills_can_teach', 'skills_want_to_learn', 'city')