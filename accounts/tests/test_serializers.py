from ..serializers import ProfileSerializer, PlayerSerializer, UserSerializer
from ..models import Player, Profile
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from mixer.backend.django import mixer
from articles.models import Tag, Deck

User = get_user_model()


class TestUserSerializer(APITestCase):
    def setUp(self):
        self.model = User
        self.serializer_class = UserSerializer

    def test_expected_fields(self):
        instance = mixer.blend(self.model)
        serializer = self.serializer_class(instance)
        expected_fields = ['username']
        self.assertEqual(set(expected_fields), set(serializer.data.keys()))

    def test_expected_values(self):
        instance = mixer.blend(self.model)
        serializer = self.serializer_class(instance)
        expected_values = {'username': instance.username}
        self.assertEqual(expected_values, serializer.data)

    pass


class TestProfileSerializer(APITestCase):
    def setUp(self):
        self.model = Profile
        self.serializer_class = ProfileSerializer
        self.user = mixer.blend(User)
        self.expected_fields = [
            'user',
            'education',
            'interests',
            'is_complete',
            'age',
            'gender',
            'birth_date',
            'name',
            'avatar',
            'starred_decks',
            'onboarded',
        ]

    def test_expected_fields(self):
        instance = self.user.profile
        serializer = self.serializer_class(instance)
        self.assertEqual(set(self.expected_fields), set(serializer.data.keys()))

    def test_expected_values(self):
        instance = self.user.profile
        instance.birth_date = mixer.faker.date_of_birth()
        instance.save()
        serializer = self.serializer_class(instance)
        expected_values = {
            'user': instance.user.username,
            'education': instance.education,
            'interests': list(instance.interests.all()),
            'is_complete': instance.is_complete,
            'age': instance.age,
            'birth_date': instance.birth_date.strftime('%Y-%m-%d'),
            'gender': instance.gender,
            'name': instance.name,
            'avatar': instance.avatar,
            'starred_decks': list(instance.starred_decks.all()),
            'onboarded': instance.onboarded,
        }
        self.assertEqual(expected_values, serializer.data, msg="{} != {}".format(expected_values, serializer.data))


class TestPlayerSerializer(APITestCase):
    def setUp(self):
        self.model = Player
        self.serializer_class = PlayerSerializer
        self.user = mixer.blend(User)
        self.expected_fields = ['user', 'room', 'hosted_room', 'skill_rating']

    def test_expected_fields(self):
        instance = self.user.player
        serializer = self.serializer_class(instance)
        self.assertEqual(set(self.expected_fields), set(serializer.data.keys()))

    def test_expected_values(self):
        instance = self.user.player
        serializer = self.serializer_class(instance)
        expected_values = {'user': instance.user.username, 'room': None, 'hosted_room': None, 'skill_rating': 500}
        self.assertEqual(expected_values, serializer.data)
