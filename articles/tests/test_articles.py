import json
from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model
from mixer.backend.django import mixer
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.reverse import reverse
from ..models import Article
from ..serializers import ArticleSerializer

User = get_user_model()


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

        self.list_endpoint = reverse('article-list')
        self.retrieve_endpoint = reverse('article-detail', kwargs={'pk': self.article.pk})

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
        response = self.retrieve_article(status.HTTP_200_OK)

    def test_noauth_add_article(self):
        response = self.create_article(status.HTTP_401_UNAUTHORIZED)

    def test_noauth_edit_article(self):
        response = self.update_article(status.HTTP_401_UNAUTHORIZED)

    def test_noauth_delete_article(self):
        response = self.delete_article(status.HTTP_401_UNAUTHORIZED)

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

    # endregion


class TestManageArticle(APITestCase):
    def setUp(self):
        self.can_manage_articles = Permission.objects.filter(content_type__model='article')
        self.manager = mixer.blend(User)
        self.manager.user_permissions.add(*self.can_manage_articles)
        self.client.force_login(self.manager)
        self.article = mixer.blend(Article)
        self.article.save()
        self.list_endpoint = reverse('article-list')

    @classmethod
    def get_nonexistent_pks(cls, num=10, fn=mixer.faker.big_integer):
        assert num > 0
        nonexistent = []
        existing = cls.get_existing_pks()
        while num:
            pk = fn()
            if pk in existing:
                num += 1
                continue
            nonexistent.append(pk)
            num -= 1
        return nonexistent

    @classmethod
    def get_existing_pks(cls):
        return [article.pk for article in Article.objects.all()]

    def get_retrieve_endpoint(self, pk=None):
        if pk is None:
            pk = self.article.pk
        return reverse('article-detail', kwargs={'pk': pk})

    def list_article(self, expected_status):
        response = self.client.get(self.list_endpoint)
        self.assertEqual(response.status_code, expected_status, response.content)
        return response

    def add_article(self, expected_status):
        new_article = mixer.blend(Article)
        response = self.client.post(self.list_endpoint, data=ArticleSerializer(new_article).data)
        self.assertEqual(response.status_code, expected_status, response.content)
        if status.is_success(expected_status):
            saved_article = Article.objects.get(pk=new_article.pk)
            self.assertEqual(saved_article.headline, new_article.headline)
        return response

    def retrieve_article(self, expected_status, pk=None):
        response = self.client.get(self.get_retrieve_endpoint(pk))
        self.assertEqual(response.status_code, expected_status, response.content)
        if status.is_success(expected_status):
            self.assertEqual(self.article.pk, json.loads(response.content)['pk'])
        return response

    def update_article(self, expected_status, pk=None):
        new_headline = 'new headline'
        data = ArticleSerializer(self.article).data
        data['headline'] = new_headline
        response = self.client.put(self.get_retrieve_endpoint(pk), data=data)
        self.assertEqual(response.status_code, expected_status, response.content)
        if status.is_success(expected_status):
            self.assertEqual(Article.objects.get(pk=self.article.pk).headline, new_headline)
        return response

    def update_article_incomplete(self, pk=None):
        new_headline = 'new headline'
        response = self.client.put(self.get_retrieve_endpoint(pk), data={'headline': new_headline})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.content)
        return response

    def partial_update_article(self, expected_status, pk=None):
        new_headline = 'new headline'
        response = self.client.patch(self.get_retrieve_endpoint(pk), data={'headline': new_headline})
        self.assertEqual(response.status_code, expected_status, response.content)
        if status.is_success(expected_status):
            self.assertEqual(Article.objects.get(pk=self.article.pk).headline, new_headline)
        return response

    def delete_article(self, expected_status, pk=None):
        response = self.client.delete(self.get_retrieve_endpoint(pk))
        self.assertEqual(response.status_code, expected_status, response.content)
        if status.is_success(expected_status):
            self.assertFalse(Article.objects.filter(pk=self.article.pk).exists())
        return response

    # region success
    def test_list_article(self):
        response = self.list_article(status.HTTP_200_OK)

    def test_add_article(self):
        response = self.add_article(status.HTTP_201_CREATED)

    def test_retrieve_article(self):
        response = self.retrieve_article(status.HTTP_200_OK)

    def test_update_article(self):
        response = self.update_article(status.HTTP_200_OK)

    def test_partial_update(self):
        response = self.partial_update_article(status.HTTP_200_OK)

    def test_delete(self):
        response = self.delete_article(status.HTTP_204_NO_CONTENT)

    # endregion

    # region failure
    def test_update_article_incomplete(self):
        for pk in self.get_existing_pks():
            response = self.update_article_incomplete(pk=pk)

    def test_update_nonexistent(self):
        for pk in self.get_nonexistent_pks(100):
            response = self.update_article(status.HTTP_404_NOT_FOUND, pk=pk)

    def test_retrieve_nonexistent(self):
        for pk in self.get_nonexistent_pks(100):
            response = self.retrieve_article(status.HTTP_404_NOT_FOUND, pk=pk)

    def test_delete_nonexistent(self):
        for pk in self.get_nonexistent_pks(100):
            response = self.delete_article(status.HTTP_404_NOT_FOUND, pk=pk)
    # endregion
