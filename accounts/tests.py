from django.test import TestCase

from .models import User

class UserManagerTestCase(TestCase):
    def setUp(self):
        User.objects.create_user(email='testuser@example.com', password='password')

    def test_user_create(self):
        user = User.objects.get(email='testuser@example.com')
        self.assertEqual(user.email, 'testuser@example.com')

