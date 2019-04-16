from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    thumbnail_url = models.URLField(max_length=1000, blank=True)


class Article(models.Model):
    headline = models.CharField(max_length=500)
    text = models.TextField(blank=True)
    truth_value = models.BooleanField(null=True, blank=True, default=None)
    rating = models.CharField(max_length=50, blank=True)
    domain = models.URLField(blank=True)
    url = models.URLField(max_length=1000, blank=True)
    thumbnail_url = models.URLField(max_length=1000, blank=True)
    author = models.CharField(max_length=100, blank=True)
    tags = models.ManyToManyField(Tag, related_name='articles', blank=True)
    explanation = models.TextField(blank=True)
    published = models.DateTimeField(null=True, blank=True)


class Deck(models.Model):
    title = models.CharField(max_length=100, unique=True)
    articles = models.ManyToManyField(Article, related_name='decks')
    description = models.CharField(max_length=200, blank=True)
    thumbnail_url = models.URLField(max_length=500, blank=True)
    tags = models.ManyToManyField(Tag, related_name='tags', blank=True, editable=False)

    # Has a 'starrers' M2M relation in accounts.profile
    # Has a 'finishers' M2M relation in accounts.profile
