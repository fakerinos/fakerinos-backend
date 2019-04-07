"""
1. Populate Articles
2. Create Deck
    a. Create links
        further: how? filter?
3. Check Deck --> assert(deck.size)
"""

from ..models import Article, Deck
from ..serializers import ArticleSerializer, DeckSerializer
from rest_framework.test import APITestCase
from rest_framework import status
from mixer.backend.django import mixer
from rest_framework.reverse import reverse
from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model

User = get_user_model()


class TestDeckAPI(APITestCase):
    # Test API

    def setUp(self):
        # Permissions
        self.can_manage_articles = Permission.objects.filter(content_type__model='deck')
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
        self.true_article = mixer.blend(Article)
        self.false_article = mixer.blend(Article)

        # Decks
        self.deck = mixer.blend(Deck)

    # TODO: move these tests to test_models.py
    def test_article_created(self):
        self.assertEqual(Article.objects.count(), 2)

    def test_deck_created(self):
        self.assertEqual(Deck.objects.count(), 1)

    def test_link_deck_to_articles(self):
        self.client.force_login(self.adder)
        self.deck.articles.add(self.true_article)
        self.deck.articles.add(self.false_article)
        self.assertEqual(set(self.deck.articles.all()), {self.true_article, self.false_article})

    # TODO: move these tests to test_views.py
    # Unit Routing Tests
    def test_routing_works(self):
        response = self.client.get(reverse('deck-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_deck(self):
        response = self.client.get(reverse('deck-detail', kwargs={'pk': self.deck.pk}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_specifically(self):
        self.client.force_login(self.adder)
        # self.deck.articles.add(self.true_article)
        # self.deck.articles.add(self.false_article)
        # response = self.client.get(reverse('deck-name') + 'test')
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
