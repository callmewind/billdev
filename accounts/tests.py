from django.test import TestCase


class UserManagerTestCase(TestCase):
    def setUp(self):
        from django.test import Client
        self.client = Client()


    def test_user_registration(self):
        from django.core import mail
        from django.urls import reverse

        #Load login page
        response = self.client.get(reverse('accounts:sign-up'))
        self.assertEqual(response.status_code, 200)

        #Post registration form
        response = self.client.post(reverse('accounts:sign-up'), {
            'first_name' : 'test_first_name',
            'last_name' : 'test_last_name',
            'email' : 'test_email@example.com',
            'password' : 'test_password',
        })
        self.assertContains(response, 'Please review your inbox and follow the link in the mail to enable your account', count=1, status_code=200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Activate your account')

        from .views import ActivateAccountTokenGenerator, ActivateView
        from .models import User
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes

        user = User.objects.get(email='test_email@example.com')

        token_generator = ActivateAccountTokenGenerator()
        activation_link = response.wsgi_request.build_absolute_uri(
            reverse('accounts:activate', kwargs={ 
                'uidb64' : urlsafe_base64_encode(force_bytes(user.pk)).decode(), 
                'token': token_generator.make_token(user) 
            })
        )
        #Check activation link
        self.assertIn(mail.outbox[0].body, activation_link)

        #Follow activation link
        from django.shortcuts import resolve_url
        response = self.client.get(activation_link)
        print(activation_link)
        self.assertRedirects(response, resolve_url(ActivateView.url))

        from django.contrib import auth
        user = auth.get_user(self.client)
        self.assertIs(user.is_authenticated, True)

        self.client.session.flush()
        response = self.client.get(activation_link)      

        self.assertEqual(response.status_code, 404)

