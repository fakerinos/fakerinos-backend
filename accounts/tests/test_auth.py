from django.contrib.auth.models import User
from mixer.backend.django import mixer
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status


# Create your tests here.
class TestRegister(APITestCase):
    default_username = mixer.faker.simple_profile()['username']
    default_email = mixer.faker.email()
    default_password = mixer.faker.password()

    def register(self, **kwargs):
        body = {
            'username': self.default_username,
            'email': self.default_email,
            'password1': self.default_password,
            'password2': self.default_password,
        }
        # add args to body
        body.update(kwargs)
        # remove None items
        nones = [k for k in body if body[k] is None]
        for k in nones:
            del body[k]
        return self.client.post(reverse('rest_register'), body, format='json')

    def test_success(self):
        response = self.register()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)

    def test_password_mismatch(self):
        response = self.register(password1='ComplexSecret', password2='ComplexSecrer')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.content)

    def test_password_too_short(self):
        response = self.register(password1='a', password2='a')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.content)

    def test_missing_password(self):
        response = self.register(password1=None, password2=None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.content)

# TODO: Test Login/out, Email Verification, etc.
