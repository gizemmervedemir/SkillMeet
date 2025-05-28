from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import MeetingProposal, Venue, MatchRequest

class ModelTests(TestCase):
    def setUp(self):
        self.user1 = get_user_model().objects.create_user(username="proposer", password="12345678")
        self.user2 = get_user_model().objects.create_user(username="receiver", password="12345678")
        self.match = MatchRequest.objects.create(sender=self.user1, receiver=self.user2)

    def test_str_meeting_proposal(self):
        meeting = MeetingProposal.objects.create(
            match=self.match,
            proposer=self.user1,
            location="Test Cafe",
            datetime="2025-06-01T12:00:00Z",
            status="pending"
        )
        expected = f"{self.match.sender} ⇄ {self.match.receiver} on {meeting.datetime} ({meeting.status})"
        self.assertEqual(str(meeting), expected)

    def test_str_venue(self):
        venue = Venue.objects.create(
            name="Cool Place",
            address="123 Street",
            city="Kadıköy",
            capacity=10
        )
        self.assertEqual(str(venue), "Cool Place - Kadıköy")

    def test_user_creation(self):
        self.assertEqual(self.user1.username, "proposer")
        self.assertTrue(self.user1.check_password("12345678"))