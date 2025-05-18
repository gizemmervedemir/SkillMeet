from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class CustomUser(AbstractUser):
    bio = models.TextField(blank=True)
    skills_can_teach = models.TextField(blank=True)  # Example: "guitar,piano"
    skills_want_to_learn = models.TextField(blank=True)  # Example: "English"
    city = models.CharField(max_length=100, blank=True)
    is_approved = models.BooleanField(default=False)
    dojo_level = models.CharField(max_length=20, default="White Belt")  # Badge system

    def __str__(self):
        return self.username

    def update_dojo_level(self):
        ratings = self.received_ratings.all()
        total = ratings.count()
        if total == 0:
            self.dojo_level = "White Belt"
            return

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
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_requests'
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_requests'
    )
    message = models.TextField(blank=True)
    is_accepted = models.BooleanField(null=True)  # None = pending, True = accepted, False = rejected
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "Accepted" if self.is_accepted else "Pending" if self.is_accepted is None else "Rejected"
        return f"{self.sender.username} → {self.receiver.username} ({status})"


class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )
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
    rater = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='given_ratings'
    )
    rated_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_ratings'
    )
    score = models.IntegerField()  # 1 to 5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rater.username} → {self.rated_user.username}: {self.score}"