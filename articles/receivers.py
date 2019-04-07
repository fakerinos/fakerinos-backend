from django.contrib.auth import get_user_model
from django.db.models import signals
from django.dispatch import receiver
from .models import Deck, Article, Tag

User = get_user_model()


@receiver(signals.m2m_changed, sender=Deck.articles.through)
def deck_articles_changed(sender, **kwargs):
    action = kwargs.pop('action')
    instance = kwargs.pop('instance', None)
    if instance and action == 'post_add':
        update_deck_tags(instance)
        instance.save()


@receiver(signals.m2m_changed, sender=Article.tags.through)
def article_tags_changed(sender, **kwargs):
    action = kwargs.pop('action')
    instance = kwargs.pop('instance', None)
    if instance and action == 'post_add':
        for deck in instance.decks.all():
            update_deck_tags(deck)
            deck.save()


def update_deck_tags(deck):
    articles = deck.articles.all()
    if articles.exists():
        new_tags = articles.exclude(tags=None).values_list('tags', flat=True)
        deck.tags.set(new_tags)
