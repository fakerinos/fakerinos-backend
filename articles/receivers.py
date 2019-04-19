from django.contrib.auth import get_user_model
from django.db.models import signals
from django.dispatch import receiver
from .models import Deck, Article, Tag
from rooms.signals import article_swiped
import logging

User = get_user_model()


@receiver(signals.m2m_changed, sender=Deck.articles.through)
def deck_articles_changed(sender, **kwargs):
    instance = kwargs.pop('instance', None)
    action = kwargs.pop('action')
    if instance and action.startswith('post_'):
        logging.info("Articles in deck {} changed".format(instance.pk))
        update_deck_tags(instance)


@receiver(signals.m2m_changed, sender=Article.tags.through)
def article_tags_changed(sender, **kwargs):
    instance = kwargs.pop('instance', None)
    action = kwargs.pop('action')
    if instance and action.startswith('post_'):
        logging.info("Tags changed on article {}".format(instance.pk))
        for deck in instance.decks.all():
            update_deck_tags(deck)


def update_deck_tags(deck):
    articles = deck.articles.all()
    if articles.exists():
        logging.info("Updating tags for deck {}".format(deck.pk))
        new_tags = articles.exclude(tags=None).values_list('tags', flat=True)
        deck.tags.set(new_tags)
