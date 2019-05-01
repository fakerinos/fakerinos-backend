from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework import status
from mixer.backend.django import mixer
from ..models import LeaderBoardStaleMarker

User = get_user_model()


class TestSinglePlayer(APITestCase):
    def setUp(self):
        self.player = mixer.blend(User)
        self.base_top_endpoint = 'leaderboard-top-'
        self.base_relative_endpoint = 'leaderboard-relative-'

    # region helpers
    def get_leaderboard(self, window, relative=False):
        self.client.force_login(self.player)
        endpoint = reverse((self.base_relative_endpoint if relative else self.base_top_endpoint) + window)
        return self.client.get(endpoint)

    def test_top_all(self):
        response = self.get_leaderboard('all')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_top_day(self):
        response = self.get_leaderboard('day')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_top_week(self):
        response = self.get_leaderboard('week')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_top_month(self):
        response = self.get_leaderboard('month')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_relative_all(self):
        response = self.get_leaderboard('all', relative=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_relative_day(self):
        response = self.get_leaderboard('day', relative=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_relative_week(self):
        response = self.get_leaderboard('week', relative=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_relative_month(self):
        response = self.get_leaderboard('month', relative=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
