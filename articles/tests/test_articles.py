from django.contrib.auth.models import User, Permission
from mixer.backend.django import mixer
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.reverse import reverse
from ..models import Article
from ..serializers import ArticleSerializer


class TestArticlePermissions(APITestCase):
    def setUp(self):
        # Permissions
        self.can_manage_articles = Permission.objects.filter(content_type__model='article')
        self.can_add_articles = self.can_manage_articles.get(codename__contains='add')
        self.can_view_articles = self.can_manage_articles.get(codename__contains='view')

        # Users
        self.viewer = mixer.blend(User)
        self.viewer.user_permissions.add(self.can_view_articles)
        self.adder = mixer.blend(User)
        self.adder.user_permissions.add(self.can_add_articles)
        self.manager = mixer.blend(User)
        self.manager.user_permissions.add(*self.can_manage_articles)

        # Articles
        self.article = mixer.blend(Article)
        self.article.save()

        self.list_endpoint = reverse('articles-list')
        self.retrieve_endpoint = reverse('articles-detail', kwargs={'pk': self.article.pk})

    # region helpers
    def retrieve_article(self, expected_status, user=None):
        if user:
            self.client.force_login(user)
        response = self.client.get(self.retrieve_endpoint)
        self.assertEqual(response.status_code, expected_status, response.content)
        return response

    def create_article(self, expected_status, user=None):
        if user:
            self.client.force_login(user)
        new_article = mixer.blend(Article)
        response = self.client.post(self.list_endpoint, data=ArticleSerializer(new_article).data)
        self.assertEqual(response.status_code, expected_status, response.content)
        return response

    def update_article(self, expected_status, user=None):
        if user:
            self.client.force_login(user)
        new_headline = 'new headline'
        data = ArticleSerializer(self.article).data
        data['headline'] = new_headline
        response = self.client.put(self.retrieve_endpoint, data=data)
        self.assertEqual(response.status_code, expected_status, response.content)
        if status.is_success(expected_status):
            self.assertEqual(Article.objects.get(pk=self.article.pk).headline, new_headline)
        return response

    def delete_article(self, expected_status, user=None):
        if user:
            self.client.force_login(user)
        response = self.client.delete(self.retrieve_endpoint)
        self.assertEqual(response.status_code, expected_status, response.content)
        return response

    # endregion

    # region no-auth
    def test_noauth_get_article(self):
        response = self.retrieve_article(status.HTTP_403_FORBIDDEN)

    def test_noauth_add_article(self):
        response = self.create_article(status.HTTP_403_FORBIDDEN)

    def test_noauth_edit_article(self):
        response = self.update_article(status.HTTP_403_FORBIDDEN)

    def test_noauth_delete_article(self):
        response = self.delete_article(status.HTTP_403_FORBIDDEN)

    # endregion

    # region adder
    def test_adder_get_article(self):
        response = self.retrieve_article(status.HTTP_200_OK, user=self.adder)

    def test_adder_add_article(self):
        response = self.create_article(status.HTTP_201_CREATED, user=self.adder)

    def test_adder_edit_article(self):
        response = self.update_article(status.HTTP_403_FORBIDDEN, user=self.adder)

    def test_adder_delete_article(self):
        response = self.delete_article(status.HTTP_403_FORBIDDEN, user=self.adder)

    # endregion

    # region viewer
    def test_viewer_get_article(self):
        response = self.retrieve_article(status.HTTP_200_OK, user=self.viewer)

    def test_viewer_add_article(self):
        response = self.create_article(status.HTTP_403_FORBIDDEN, user=self.viewer)

    def test_viewer_edit_article(self):
        response = self.update_article(status.HTTP_403_FORBIDDEN, user=self.viewer)

    def test_viewer_delete_article(self):
        response = self.delete_article(status.HTTP_403_FORBIDDEN, user=self.viewer)

    # endregion

    # region manager
    def test_manager_get_article(self):
        response = self.retrieve_article(status.HTTP_200_OK, user=self.manager)

    def test_manager_add_article(self):
        response = self.create_article(status.HTTP_201_CREATED, user=self.manager)

    def test_manager_edit_article(self):
        response = self.update_article(status.HTTP_200_OK, user=self.manager)

    def test_manager_delete_article(self):
        response = self.delete_article(status.HTTP_204_NO_CONTENT, user=self.manager)
