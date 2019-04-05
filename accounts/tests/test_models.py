from ..models import Profile, Player, get_anonymous_user_instance
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


class TestUser(TestCase):
    def setUp(self):
        self.model = User

    def test_profile_created(self):
        user = self.model.objects.create()
        self.assertEqual(Profile.objects.filter(pk=user).count(), 1)

    def test_player_created(self):
        user = self.model.objects.create()
        self.assertEqual(Player.objects.filter(pk=user).count(), 1)

    def test_get_anonymous_user_instance(self):
        instance = get_anonymous_user_instance(self.model)
        self.assertEqual(instance.username, settings.ANONYMOUS_USER_NAME)
