from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

# Sabit skill seçenekleri, değerler küçük harfli key, etiketler okunabilir hali
SKILL_CHOICES = [
    ('guitar', 'Guitar'),
    ('piano', 'Piano'),
    ('english', 'English'),
    ('french', 'French'),
    ('football', 'Football'),
    ('basketball', 'Basketball'),
    ('drawing', 'Drawing'),
    ('sculpting', 'Sculpting'),
    ('painting', 'Painting'),
    ('tennis', 'Tennis'),
    ('fitness', 'Fitness'),
    ('turkish', 'Turkish'),
    ('german', 'German'),
    ('violin', 'Violin'),
    ('drums', 'Drums'),
    ('singing', 'Singing'),
    ('photography', 'Photography'),
    ('coding', 'Coding'),
]

CITY_CHOICES = [
    ('Kadıköy', 'Kadıköy'),
    ('Üsküdar', 'Üsküdar'),
    ('Ataşehir', 'Ataşehir'),
    ('Maltepe', 'Maltepe'),
    ('Kartal', 'Kartal'),
    ('Pendik', 'Pendik'),
    ('Tuzla', 'Tuzla'),
    ('Sancaktepe', 'Sancaktepe'),
    ('Çekmeköy', 'Çekmeköy'),
]

# ---------------------------
# KULLANICI KAYIT FORMU
# ---------------------------

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email Address")
    profile_image = forms.ImageField(required=False, label="Profile Image")

    skills_can_teach = forms.MultipleChoiceField(
        choices=SKILL_CHOICES,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=False,
        label="Skills You Can Teach"
    )

    skills_want_to_learn = forms.MultipleChoiceField(
        choices=SKILL_CHOICES,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=False,
        label="Skills You Want to Learn"
    )

    city = forms.ChoiceField(
        choices=CITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        label="District (Istanbul)"
    )

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
            'bio',
            'profile_image',
            'skills_can_teach',
            'skills_want_to_learn',
            'city',
            'password1',
            'password2',
        )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean_skills_can_teach(self):
        skills = self.cleaned_data.get('skills_can_teach', [])
        return ','.join(skills)

    def clean_skills_want_to_learn(self):
        skills = self.cleaned_data.get('skills_want_to_learn', [])
        return ','.join(skills)


# ---------------------------
# KULLANICI PROFİL GÜNCELLEME FORMU
# ---------------------------

class CustomUserUpdateForm(forms.ModelForm):
    profile_image = forms.ImageField(required=False, label="Profile Image")

    skills_can_teach = forms.MultipleChoiceField(
        choices=SKILL_CHOICES,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=False,
        label="Skills You Can Teach"
    )

    skills_want_to_learn = forms.MultipleChoiceField(
        choices=SKILL_CHOICES,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=False,
        label="Skills You Want to Learn"
    )

    city = forms.ChoiceField(
        choices=CITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        label="District (Istanbul)"
    )

    class Meta:
        model = CustomUser
        fields = (
            'bio',
            'profile_image',
            'skills_can_teach',
            'skills_want_to_learn',
            'city',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if self.instance.skills_can_teach:
                self.initial['skills_can_teach'] = self.instance.skills_can_teach.split(',')
            if self.instance.skills_want_to_learn:
                self.initial['skills_want_to_learn'] = self.instance.skills_want_to_learn.split(',')

    def clean_skills_can_teach(self):
        skills = self.cleaned_data.get('skills_can_teach', [])
        return ','.join(skills)

    def clean_skills_want_to_learn(self):
        skills = self.cleaned_data.get('skills_want_to_learn', [])
        return ','.join(skills)