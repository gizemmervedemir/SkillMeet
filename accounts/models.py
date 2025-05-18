from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    bio = models.TextField(blank=True)
    skills_can_teach = models.TextField(blank=True)  # CSV: "gitar,piyano"
    skills_want_to_learn = models.TextField(blank=True)  # CSV: "İngilizce"
    city = models.CharField(max_length=100, blank=True)
    is_approved = models.BooleanField(default=False)
    dojo_level = models.CharField(max_length=20, default="White Belt")  # Rozet

    def __str__(self):
        return self.username