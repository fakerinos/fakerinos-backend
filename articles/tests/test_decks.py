from . import test_articles
from ..models import Article, Deck
from ..serializers import ArticleSerializer, DeckSerializer
from rest_framework.test import APITestCase
from rest_framework import status
from mixer.backend.django import mixer
from rest_framework.reverse import reverse
from django.contrib.auth.models import User, Permission

"""
1. Populate Articles
2. Create Deck
    a. Create links
        further: how? filter?
3. Check Deck --> assert(deck.size) 
"""

"""
routers --> reverse(<basename>-list) or (<basename>-detail)
you need Permissions && Users instantiated for testing routers
        # .save will only update the fields with those names
        #self.deck.save(update_fields=["articles"])
        
permissions:
"""


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
        self.article = mixer.blend(Article, headline='article1', rating='Hot Stuff')
        self.article2 = mixer.blend(Article,headline='article2', rating='Fake')

        # Decks
        self.deck = mixer.blend(Deck, subject='test')
        self.deck.save()

        # Why doesnt this work?
        Deck.objects.create(subject='test')

    # Unit Function Tests
    def test_article_instantiated(self):
        assert isinstance(self.article, Article)
        self.assertEqual(self.article.headline, "article1")
        self.assertEqual(self.article2.headline, "article2")

    def test_deck_created(self):
        decks = Deck.objects.count()
        self.assertEqual(decks, 2)

    def test_routing_works(self):
        self.client.force_login(self.adder)
        response = self.client.get(reverse('decks-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_deck(self):
        self.client.force_login(self.adder)
        response = self.client.get(reverse('decks-detail', kwargs={'pk': self.deck.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_link_deck_to_articles(self):
        self.client.force_login(self.adder)
        self.deck.articles.add(self.article)
        self.deck.articles.add(self.article2)
        self.assertEqual(self.deck.articles.all()[1].headline, "article2")

    def test_filter_through_links(self):
        self.client.force_login(self.adder)
        self.deck.articles.add(self.article)
        self.deck.articles.add(self.article2)
        self.assertEqual(self.deck.articles.all().filter(headline="article2").exists(), True)

    def test_get_article_from_filter(self):
        self.deck.articles.add(self.article)
        self.assertEqual(self.deck.articles.all().get(headline="article1").rating, "Hot Stuff")

    # Unit Routing Tests
    def test_routing_deck_to_article(self):
        self.deck.articles.add(self.article)
        self.client.force_login(self.adder)
        # TODO add custom router to hyperlink from filter
        'Serializers deal with the JSON passing of info'
        response = self.client.get()