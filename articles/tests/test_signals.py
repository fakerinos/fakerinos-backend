from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model
from mixer.backend.django import mixer
from django.db.models import signals
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.reverse import reverse
from .. import receivers
from ..models import Article, Deck, Tag
from unittest.mock import patch

User = get_user_model()


class TestDeckSignals(APITestCase):
    def setUp(self) -> None:
        self.tag1 = mixer.blend(Tag)
        self.tag2 = mixer.blend(Tag)
        self.article1 = mixer.blend(Article, tags=[self.tag1])
        self.article2 = mixer.blend(Article, tags=[self.tag2])
        self.deck = mixer.blend(Deck, articles=[self.article1])

    # region deck articles changed
    def test_deck_articles_changed_signal_sent(self):
        with patch.object(signals.m2m_changed, 'send') as mock_signal:
            self.deck.articles.set([self.article2])
            self.assertEqual(mock_signal.call_count, 4)

    def test_deck_articles_changed_signal_received(self):
        with patch.object(receivers, 'deck_articles_changed') as mock_receiver:
            signals.m2m_changed.connect(mock_receiver, sender=Deck.articles.through)
            self.deck.articles.set([self.article2])
            self.assertEqual(mock_receiver.call_count, 4)

    def test_deck_articles_changed_updater_called(self):
        with patch.object(receivers, 'update_deck_tags') as mock_updater:
            self.deck.articles.set([self.article2])
            self.assertEqual(mock_updater.call_count, 2)

    def test_deck_articles_changed_deck_tags_updated(self):
        self.deck.articles.set([self.article2])
        self.assertEqual(set(self.deck.tags.all()), {self.tag2})

    # endregion

    # region article tags changed
    def test_article_tags_changed_signal_sent(self):
        with patch.object(signals.m2m_changed, 'send') as mock_signal:
            self.article1.tags.set([self.tag2])
            self.assertEqual(mock_signal.call_count, 4)

    def test_article_tags_changed_signal_received(self):
        with patch.object(receivers, 'article_tags_changed') as mock_receiver:
            signals.m2m_changed.connect(mock_receiver, sender=Article.tags.through)
            self.article1.tags.set([self.tag2])
            self.assertEqual(mock_receiver.call_count, 4)

    def test_article_tags_changed_updater_called(self):
        with patch.object(receivers, 'update_deck_tags') as mock_updater:
            self.article1.tags.set([self.tag2])
            self.assertEqual(mock_updater.call_count, 2)

    def test_article_tags_changed_deck_tags_updated(self):
        self.article1.tags.set([self.tag2])
        self.assertEqual(set(self.deck.tags.all()), {self.tag2})

    # endregion
