from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)  # Email zorunlu olsun diye

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'bio', 'skills_can_teach', 'skills_want_to_learn', 'city')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu email zaten kayıtlı.")
        return email


class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('bio', 'skills_can_teach', 'skills_want_to_learn', 'city')