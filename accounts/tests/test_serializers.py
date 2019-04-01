from ..serializers import ProfileSerializer, PlayerSerializer, UserSerializer
from ..models import Player, Profile
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from mixer.backend.django import mixer
from articles.models import Tag

User = get_user_model()


class TestUserSerializer(APITestCase):
    def setUp(self):
        self.model = User
        self.serializer_class = UserSerializer
        self.expected_values = {'pk': 1}
        self.expected_fields = ['pk']

    def test_expected_fields(self):
        instance = mixer.blend(self.model)
        serializer = self.serializer_class(instance)
        self.assertEqual(set(self.expected_fields), set(serializer.data.keys()))

    def test_expected_values(self):
        instance = mixer.blend(self.model)
        serializer = self.serializer_class(instance)
        self.assertEqual(self.expected_values, serializer.data)

    pass


class TestProfileSerializer(APITestCase):
    def setUp(self):
        self.model = Profile
        self.serializer_class = ProfileSerializer
        self.user = mixer.blend(User)
        self.expected_fields = ['pk', 'education', 'interests', 'is_complete']
        self.expected_values = {'pk': 1, 'education': 'Unknown', 'interests': Tag.objects.none(), 'is_complete': False}

    def test_expected_fields(self):
        instance = self.user.profile
        serializer = self.serializer_class(instance)
        self.assertEqual(set(self.expected_fields), set(serializer.data.keys()))

    # def test_expected_values(self):
    #     instance = self.user.profile
    #     serializer = self.serializer_class(instance)
    #     print(serializer.data['interests'])
    #     self.assertEqual(self.expected_values, serializer.data)


class TestPlayerSerializer(APITestCase):
    def setUp(self):
        self.model = Player
        self.serializer_class = PlayerSerializer
        self.user = mixer.blend(User)
        self.expected_fields = ['pk', 'room', 'hosted_room', 'score']
        self.expected_values = {'pk': 1, 'room': None, 'hosted_room': None, 'score': 0}

    def test_expected_fields(self):
        instance = self.user.player
        serializer = self.serializer_class(instance)
        self.assertEqual(set(self.expected_fields), set(serializer.data.keys()))

    def test_expected_values(self):
        instance = self.user.player
        serializer = self.serializer_class(instance)
        self.assertEqual(self.expected_values, serializer.data)
