from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

class ViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", email="test@test.com", password="12345678"
        )

    def test_register_view_loads(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Register")

    def test_login_view_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_profile_requires_login(self):
        response = self.client.get(reverse('profile'))
        self.assertRedirects(response, "/login/?next=/profile/")

    def test_profile_authenticated(self):
        self.client.login(username="testuser", password="12345678")
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)