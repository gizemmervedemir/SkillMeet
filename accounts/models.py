from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class CustomUser(AbstractUser):
    bio = models.TextField(blank=True)

    profile_image = models.ImageField(
        upload_to='profile_images/',
        default='profile_images/default_avatar.png',
        blank=True,
        null=True
    )

    skills_can_teach = models.TextField(blank=True)
    skills_want_to_learn = models.TextField(blank=True)

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
    city = models.CharField(max_length=100, choices=CITY_CHOICES, default='Kadıköy')

    is_approved = models.BooleanField(default=False)
    dojo_level = models.CharField(max_length=20, default="White Belt")

    CATEGORY_CHOICES = [
        ("sports", "Sports"),
        ("art", "Art"),
        ("language", "Language"),
        ("music", "Music"),
        ("others", "Others"),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="others")

    def __str__(self):
        return self.username

    def update_dojo_level(self):
        ratings = self.received_ratings.all()
        total = ratings.count()

        if total == 0:
            self.dojo_level = "White Belt"
        else:
            avg = sum(r.score for r in ratings) / total
            if total >= 10 and avg >= 4.8:
                self.dojo_level = "Master"
            elif avg >= 4.6:
                self.dojo_level = "Red Belt"
            elif avg >= 4.0:
                self.dojo_level = "Blue Belt"
            elif avg >= 3.0:
                self.dojo_level = "Yellow Belt"
            else:
                self.dojo_level = "White Belt"
        self.save()


class MatchRequest(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_requests')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_requests')
    message = models.TextField(blank=True)
    is_accepted = models.BooleanField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "Accepted" if self.is_accepted else "Pending" if self.is_accepted is None else "Rejected"
        return f"{self.sender.username} → {self.receiver.username} ({status})"


class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username} at {self.timestamp:%Y-%m-%d %H:%M}"


class MeetingProposal(models.Model):
    match = models.ForeignKey(MatchRequest, on_delete=models.CASCADE)
    proposer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    datetime = models.DateTimeField()
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.match.sender} ⇄ {self.match.receiver} on {self.datetime} ({self.status})"


class Rating(models.Model):
    rater = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='given_ratings')
    rated_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_ratings')
    score = models.IntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rater.username} → {self.rated_user.username}: {self.score}"


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"To {self.user.username}: {self.message} ({'read' if self.is_read else 'unread'})"


class PartnerCompany(models.Model):
    TYPE_CHOICES = [
        ("place", "Place for Meeting"),
        ("company", "Corporate Partner"),
    ]
    name = models.CharField(max_length=255)
    contact_email = models.EmailField()
    website = models.URLField(blank=True)
    discount_details = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="company")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Venue(models.Model):
    VENUE_TYPE_CHOICES = [
        ('place', 'Meeting Place'),
        ('company', 'Discount Provider'),
    ]

    name = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    available_for_teaching = models.BooleanField(default=True)
    contact_person = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(blank=True)
    logo = models.ImageField(upload_to="venue_logos/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    type = models.CharField(max_length=20, choices=VENUE_TYPE_CHOICES, default="place")

    def __str__(self):
        return f"{self.name} - {self.city}"


class MarketingCampaign(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    platform = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title