import json
from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model
from mixer.backend.django import mixer
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.reverse import reverse
from fakerinos.tests.helpers import ModelViewSetHelpersMixin
from ..models import Article, Deck, Tag
from ..serializers import ArticleSerializer, DeckSerializer, TagSerializer

User = get_user_model()


class TestArticlePermissions(ModelViewSetHelpersMixin, APITestCase):
    list_endpoint = 'article-list'
    detail_endpoint = 'article-detail'
    model = Article
    serializer_class = ArticleSerializer

    def setUp(self):
        # Permissions
        self.can_manage_articles = Permission.objects.filter(content_type__model='article')
        self.can_add_articles = self.can_manage_articles.get(codename__contains='add')

        # Users
        self.viewer = mixer.blend(User)
        self.adder = mixer.blend(User)
        self.adder.user_permissions.add(self.can_add_articles)
        self.manager = mixer.blend(User)
        self.manager.user_permissions.add(*self.can_manage_articles)

        # Articles
        self.article = mixer.blend(Article)

    # region no-auth
    def test_noauth_list(self):
        self.list(status.HTTP_200_OK)

    def test_noauth_retrieve(self):
        self.retrieve(status.HTTP_200_OK, lookup=self.article.pk)

    def test_noauth_add(self):
        self.create(status.HTTP_401_UNAUTHORIZED)

    def test_noauth_edit(self):
        self.update(status.HTTP_401_UNAUTHORIZED, lookup=self.article.pk)

    def test_noauth_delete(self):
        self.delete(status.HTTP_401_UNAUTHORIZED, lookup=self.article.pk)

    # endregion

    # region adder
    def test_adder_list(self):
        self.list(status.HTTP_200_OK, user=self.adder)

    def test_adder_retrieve(self):
        self.retrieve(status.HTTP_200_OK, user=self.adder, lookup=self.article.pk)

    def test_adder_add(self):
        self.create(status.HTTP_201_CREATED, user=self.adder)

    def test_adder_edit(self):
        self.update(status.HTTP_403_FORBIDDEN, user=self.adder, lookup=self.article.pk)

    def test_adder_delete(self):
        self.delete(status.HTTP_403_FORBIDDEN, user=self.adder, lookup=self.article.pk)

    # endregion

    # region viewer
    def test_viewer_list(self):
        self.list(status.HTTP_200_OK, user=self.viewer)

    def test_viewer_retrieve(self):
        self.retrieve(status.HTTP_200_OK, user=self.viewer, lookup=self.article.pk)

    def test_viewer_add(self):
        self.create(status.HTTP_403_FORBIDDEN, user=self.viewer)

    def test_viewer_edit(self):
        self.update(status.HTTP_403_FORBIDDEN, user=self.viewer, lookup=self.article.pk)

    def test_viewer_delete(self):
        self.delete(status.HTTP_403_FORBIDDEN, user=self.viewer, lookup=self.article.pk)

    # endregion

    # region manager
    def test_manager_list(self):
        self.list(status.HTTP_200_OK, user=self.manager)

    def test_manager_retrieve(self):
        self.retrieve(status.HTTP_200_OK, user=self.manager, lookup=self.article.pk)

    def test_manager_add(self):
        self.create(status.HTTP_201_CREATED, user=self.manager)

    def test_manager_edit(self):
        self.update(status.HTTP_200_OK, user=self.manager, lookup=self.article.pk)

    def test_manager_delete(self):
        self.delete(status.HTTP_204_NO_CONTENT, user=self.manager, lookup=self.article.pk)

    # endregion


class TestDeckRecommendations(ModelViewSetHelpersMixin, APITestCase):
    list_endpoint = 'deck-list'
    detail_endpoint = 'deck-detail'
    model = Deck
    serializer_class = DeckSerializer

    def setUp(self) -> None:
        self.tags = mixer.cycle(20).blend(Tag)
        self.admin = mixer.blend(User, is_superuser=True)
        self.user = mixer.blend(User)
        self.user.profile.interests.set(self.tags[:5])
        self.user.profile.save()
        self.articles = mixer.cycle(100).blend(Article, tags=mixer.sequence(*self.tags))
        self.decks = mixer.cycle(30).blend(Deck, articles=mixer.sequence(*self.articles))

    # region helpers
    def test_recommended_decks_endpoint(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('deck-recommended'))
        recommended_decks = json.loads(response.content)
        self.assertLessEqual(len(recommended_decks), 10)

    def test_recommended_decks_algorithm(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('deck-recommended'))
        recommended_decks = json.loads(response.content)
        for deck in recommended_decks:
            deck = Deck.objects.get(id=deck['pk'])
            deck_tags = set(deck.tags.all())
            interests = set(self.user.profile.interests.all())
            self.assertTrue(deck_tags.intersection(interests))

    def test_get_trending_decks(self):
        response = self.client.get(reverse('deck-trending'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_poll(self):
        self.client.force_login(self.user)
        article = mixer.blend(Article, is_poll=True)
        response = self.client.get(reverse('deck-poll'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_mark_finished(self):
        self.client.force_login(self.admin)
        deck = mixer.blend(Deck)
        response = self.client.post(reverse('deck-mark-finished', kwargs={'pk': deck.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_star_and_unstar(self):
        self.client.force_login(self.admin)
        deck = mixer.blend(Deck)
        response = self.client.post(reverse('deck-star', kwargs={'pk': deck.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_remake_decks(self):
        self.client.force_login(self.admin)
        tag = mixer.blend(Tag)
        article = mixer.blend(Article)
        article.tags.add(tag)
        deck = mixer.blend(Deck)
        deck.articles.add(article)
        response = self.client.post(reverse('deck-remake-decks'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
