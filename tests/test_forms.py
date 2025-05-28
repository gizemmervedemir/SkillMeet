from django.test import TestCase
from accounts.forms import CustomUserCreationForm

class FormTests(TestCase):
    def test_valid_registration_form(self):
        form_data = {
            "username": "newuser",
            "email": "new@user.com",
            "password1": "StrongPass123",
            "password2": "StrongPass123",
            "city": "Kadıköy",
            "category": "sports"
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_password_mismatch(self):
        form_data = {
            "username": "mismatch",
            "email": "mismatch@user.com",
            "password1": "StrongPass123",
            "password2": "WrongPass123",
            "city": "Kadıköy",
            "category": "sports"
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_missing_category(self):
        form_data = {
            "username": "nousercat",
            "email": "no@cat.com",
            "password1": "StrongPass123",
            "password2": "StrongPass123",
            "city": "Kadıköy"
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("category", form.errors)