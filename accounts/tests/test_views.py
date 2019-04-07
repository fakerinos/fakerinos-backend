from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework import status
from mixer.backend.django import mixer
from fakerinos.tests.helpers import ModelViewSetHelpersMixin
from ..models import Player, Profile
from ..serializers import UserSerializer, PlayerSerializer, ProfileSerializer

User = get_user_model()


class TestUserViewSet(ModelViewSetHelpersMixin, APITestCase):
    list_endpoint = 'user-list'
    detail_endpoint = 'user-detail'
    model = User
    serializer_class = UserSerializer
    lookup_field = 'username'

    def setUp(self) -> None:
        self.user = mixer.blend(User)
        self.admin = mixer.blend(User, is_superuser=True)

    # region noauth
    def test_noauth_list(self):
        self.list(status.HTTP_401_UNAUTHORIZED)

    def test_noauth_retrieve(self):
        self.retrieve(status.HTTP_401_UNAUTHORIZED, lookup=self.user.username)

    def test_noauth_create(self):
        self.create(status.HTTP_401_UNAUTHORIZED)

    def test_noauth_update(self):
        self.update(status.HTTP_401_UNAUTHORIZED, lookup=self.user.username)

    def test_noauth_partial_update(self):
        self.partial_update(status.HTTP_401_UNAUTHORIZED, lookup=self.user.username)

    def test_noauth_delete(self):
        self.delete(status.HTTP_401_UNAUTHORIZED, lookup=self.user.username)

    # endregion

    # region user
    def test_player_list(self):
        self.list(status.HTTP_200_OK, user=self.user)

    def test_player_retrieve(self):
        self.retrieve(status.HTTP_200_OK, lookup=self.user.username, user=self.user)

    def test_player_create(self):
        self.create(status.HTTP_405_METHOD_NOT_ALLOWED, user=self.user)

    def test_player_update(self):
        self.update(status.HTTP_405_METHOD_NOT_ALLOWED, lookup=self.user.username, user=self.user)

    def test_player_partial_update(self):
        self.partial_update(status.HTTP_405_METHOD_NOT_ALLOWED, lookup=self.user.username, user=self.user)

    def test_player_delete(self):
        self.delete(status.HTTP_405_METHOD_NOT_ALLOWED, lookup=self.user.username, user=self.user)

    # endregion

    # region admin
    def test_admin_list(self):
        self.list(status.HTTP_200_OK, user=self.admin)

    def test_admin_retrieve(self):
        self.retrieve(status.HTTP_200_OK, lookup=self.admin.username, user=self.admin)

    def test_admin_create(self):
        self.create(status.HTTP_405_METHOD_NOT_ALLOWED, user=self.admin)

    def test_admin_update(self):
        self.update(status.HTTP_405_METHOD_NOT_ALLOWED, lookup=self.admin.username, user=self.admin)

    def test_admin_update_other(self):
        self.update(status.HTTP_405_METHOD_NOT_ALLOWED, lookup=self.user.username, user=self.admin)

    def test_admin_partial_update(self):
        self.partial_update(status.HTTP_405_METHOD_NOT_ALLOWED, lookup=self.admin.username, user=self.admin)

    def test_admin_partial_update_other(self):
        self.partial_update(status.HTTP_405_METHOD_NOT_ALLOWED, lookup=self.user.username, user=self.admin)

    def test_admin_delete(self):
        self.delete(status.HTTP_405_METHOD_NOT_ALLOWED, lookup=self.admin.username, user=self.admin)
    # endregion


class TestPlayerViewSet(APITestCase):
    pass


class TestProfileViewSet(ModelViewSetHelpersMixin, APITestCase):
    list_endpoint = 'profile-list'
    detail_endpoint = 'profile-detail'
    model = Profile
    serializer_class = ProfileSerializer
    lookup_field = 'user__username'

    def setUp(self) -> None:
        self.user = mixer.blend(User)
        self.admin = mixer.blend(User, is_superuser=True)

    # region noauth
    def test_noauth_list(self):
        self.list(status.HTTP_401_UNAUTHORIZED)

    def test_noauth_retrieve(self):
        self.retrieve(status.HTTP_401_UNAUTHORIZED, lookup=self.user.username)

    def test_noauth_create(self):
        self.create(status.HTTP_401_UNAUTHORIZED)

    def test_noauth_update(self):
        self.update(status.HTTP_401_UNAUTHORIZED, lookup=self.user.username)

    def test_noauth_partial_update(self):
        self.partial_update(status.HTTP_401_UNAUTHORIZED, lookup=self.user.username)

    def test_noauth_delete(self):
        self.delete(status.HTTP_401_UNAUTHORIZED, lookup=self.user.username)

    # endregion

    # region user
    def test_player_list(self):
        self.list(status.HTTP_200_OK, user=self.user)

    def test_player_retrieve(self):
        self.retrieve(status.HTTP_200_OK, lookup=self.user.username, user=self.user)

    def test_player_create(self):
        self.create(status.HTTP_405_METHOD_NOT_ALLOWED, user=self.user)

    def test_player_update(self):
        self.update(status.HTTP_200_OK, lookup=self.user.username, user=self.user)

    def test_player_update_other(self):
        self.update(status.HTTP_403_FORBIDDEN, lookup=self.admin.username, user=self.user)

    def test_player_partial_update(self):
        self.partial_update(status.HTTP_200_OK, lookup=self.user.username, user=self.user)

    def test_player_partial_update_other(self):
        self.partial_update(status.HTTP_403_FORBIDDEN, lookup=self.admin.username, user=self.user)

    def test_player_delete(self):
        self.delete(status.HTTP_405_METHOD_NOT_ALLOWED, lookup=self.user.username, user=self.user)

    # endregion

    # region admin
    def test_admin_list(self):
        self.list(status.HTTP_200_OK, user=self.admin)

    def test_admin_retrieve(self):
        self.retrieve(status.HTTP_200_OK, lookup=self.admin.username, user=self.admin)

    def test_admin_create(self):
        self.create(status.HTTP_405_METHOD_NOT_ALLOWED, user=self.admin)

    def test_admin_update(self):
        self.update(status.HTTP_200_OK, lookup=self.admin.username, user=self.admin)

    def test_admin_update_other(self):
        self.update(status.HTTP_200_OK, lookup=self.user.username, user=self.admin)

    def test_admin_partial_update(self):
        self.partial_update(status.HTTP_200_OK, lookup=self.admin.username, user=self.admin)

    def test_admin_partial_update_other(self):
        self.partial_update(status.HTTP_200_OK, lookup=self.user.username, user=self.admin)

    def test_admin_delete(self):
        self.delete(status.HTTP_405_METHOD_NOT_ALLOWED, lookup=self.admin.username, user=self.admin)
    # endregion
