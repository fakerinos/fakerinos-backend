from django.contrib.auth.models import User, Group, Permission
from mixer.backend.django import mixer
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse, resolve
from rest_framework.authtoken.models import Token
from rest_framework import status
from ..models import Article


class TestManageArticles(APITestCase):
    def setUp(self):
        self.can_manage_articles = Permission.objects.filter(content_type__model='article')
        self.can_add_articles = self.can_manage_articles.filter(codename__contains='add')

        self.managers = mixer.blend(Group, name='article_managers')
        self.managers.permissions.add(*self.can_manage_articles)

        self.crawlers = mixer.blend(Group, name='article_crawlers')
        self.crawlers.permissions.add(*self.can_add_articles)

        self.admin = mixer.blend(User, is_superuser=True)
        self.user = mixer.blend(User)

    # region no auth
    def test_noauth_add_article(self):
        # Should fail, but TODO: try POST request
        self.client.post(reverse('manage_articles'),
                         {}
                         )
        self.fail()

    def test_noauth_delete_article(self):
        self.fail()

    def test_noauth_edit_article(self):
        self.fail()

    def test_noauth_get_article(self):
        self.fail()

    # endregion

    # region player
    def test_player_add_article(self):
        self.fail()

    def test_player_delete_article(self):
        self.fail()

    def test_player_edit_article(self):
        self.fail()

    def test_player_get_article(self):
        self.fail()

    # endregion

    # region crawler
    def test_crawler_add_article(self):
        self.fail()

    def test_crawler_delete_article(self):
        self.fail()

    def test_crawler_edit_article(self):
        self.fail()

    def test_crawler_get_article(self):
        self.fail()

    # endregion

    # region admin
    def test_admin_add_article(self):
        self.fail()

    def test_admin_delete_article(self):
        self.fail()

    def test_admin_edit_article(self):
        self.fail()

    def test_admin_get_article(self):
        self.fail()

    # endregion


class TestGetArticles(APITestCase):
    pass
