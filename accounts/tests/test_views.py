from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework import status
from mixer.backend.django import mixer
from ..models import Player, Profile
from ..serializers import UserSerializer

User = get_user_model()


class TestUserViewSet(APITestCase):
    def setUp(self):
        self.list_endpoint = reverse('user-list')
        self.user = mixer.blend(User)
        self.user.save()

    def get_detail_endpoint(self, pk=None):
        pk = pk or self.user.pk
        return reverse('user-detail', kwargs={'pk': pk})

    def list_users(self):
        pass

    def retrieve_user(self, pk):
        pass

    def create_user(self, user=None):
        if user:
            self.client.force_login(user)
        new_user = mixer.blend(User)
        response = self.client.post(self.list_endpoint, data=UserSerializer(new_user).data)
        self.assertTrue(status.is_client_error(response.status_code))

    def update_user(self):
        pass

    def partial_update_user(self):
        pass

    def delete_user(self):
        pass

    def test_noauth_list_users(self):
        pass

    def test_noauth_retrieve_user(self):
        pass

    def test_noauth_create_user(self):
        self.create_user()

    def test_noauth_update_user(self):
        self.client.force_login(self.user)

    def test_noauth_partial_update_user(self):
        pass


class TestPlayerViewSet(APITestCase):
    pass


class TestProfileViewSet(APITestCase):
    pass
