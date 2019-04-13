from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework import status
from mixer.backend.django import mixer
from articles.models import Deck
from ..models import Room
from ..serializers import RoomSerializer

User = get_user_model()


class TestSinglePlayer(APITestCase):
    def setUp(self):
        self.room = mixer.blend(Room)
        self.player = mixer.blend(User)
        self.admin = mixer.blend(User, is_superuser=True)
        self.list_endpoint = reverse('single-player-list')

    # region helpers
    def get_detail_endpoint(self, pk):
        return reverse('single-player-detail', kwargs={'pk': pk})

    def list_rooms(self, user=None):
        if user:
            self.client.force_login(user)
        response = self.client.get(self.list_endpoint)
        return response

    def retrieve_room(self, pk, user=None):
        if user:
            self.client.force_login(user)
        response = self.client.get(self.get_detail_endpoint(pk))
        return response

    def create_room(self, user=None):
        if user:
            self.client.force_login(user)
        deck = mixer.blend(Deck)
        response = self.client.post(self.list_endpoint, data={'deck': deck.pk})
        return response

    def update_room(self, pk, data, user=None):
        if user:
            self.client.force_login(user)
        response = self.client.put(self.get_detail_endpoint(pk), data=data)
        return response

    def partial_update_room(self, pk, data, user=None):
        if user:
            self.client.force_login(user)
        response = self.client.patch(self.get_detail_endpoint(pk), data=data)
        return response

    def delete_room(self, pk, user=None):
        if user:
            self.client.force_login(user)
        response = self.client.delete(self.get_detail_endpoint(pk))
        return response

    # endregion

    # region noauth
    def test_noauth_list_rooms(self):
        response = self.list_rooms()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_noauth_retrieve_room(self):
        response = self.retrieve_room(self.room.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_noauth_create_room(self):
        response = self.create_room()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_noauth_delete_room(self):
        response = self.delete_room(self.room.pk)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_noauth_update_room(self):
        response = self.update_room(self.room.pk, {'max_players': 100, 'status': 'NEW'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_noauth_partial_update_room(self):
        response = self.partial_update_room(self.room.pk, {'max_players': 100})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # endregion

    # region player
    def test_player_list_rooms(self):
        response = self.list_rooms(user=self.player)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_player_retrieve_room(self):
    #     response = self.retrieve_room(self.room.pk, user=self.player)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_player_create_room(self):
        response = self.create_room(user=self.player)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_player_delete_room(self):
        response = self.delete_room(self.room.pk, user=self.player)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_player_update_room(self):
    #     response = self.update_room(self.room.pk, {'max_players': 100, 'status': 'NEW'}, user=self.player)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    # def test_player_partial_update_room(self):
    #     response = self.partial_update_room(self.room.pk, {'max_players': 100}, user=self.player)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_player_create_room_already_in_room(self):
        self.player.player.room = self.room
        self.player.player.save()
        response = self.create_room(user=self.player)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # endregion

    # region admin
    def test_admin_list_rooms(self):
        response = self.list_rooms(user=self.admin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_retrieve_room(self):
        response = self.retrieve_room(self.room.pk, user=self.admin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_create_room(self):
        response = self.create_room(user=self.admin)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_delete_room(self):
        response = self.delete_room(self.room.pk, user=self.admin)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_admin_update_room(self):
        response = self.update_room(self.room.pk, {'max_players': 100, 'status': 'NEW'}, user=self.admin)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_admin_partial_update_room(self):
        response = self.partial_update_room(self.room.pk, {'max_players': 100}, user=self.admin)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # endregion
