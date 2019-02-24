from django.contrib.auth.models import User, Group, Permission
from mixer.backend.django import mixer
from rest_framework.test import APITestCase
from rest_framework import status


class TestAddArticles(APITestCase):
    def test_upload_article_admin(self):
        admin = mixer.blend(User, is_staff=True, is_superuser=True)
        # TODO: Try uploading something (via POST?)

        # Should pass, but leaving this here as a reminder
        self.fail()


class TestGetArticles(APITestCase):
    pass
