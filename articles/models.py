from django.db import models
from fakerinos.models import CreatorModel


class Tag(CreatorModel):
    name = models.CharField(max_length=50)


class Article(CreatorModel):
    headline = models.CharField(max_length=500)
    rating = models.CharField(max_length=50)
    domain = models.URLField(null=True, blank=True)
    text = models.TextField(blank=True, null=True)
    thumbnail_url = models.URLField(null=True, blank=True)
    author = models.CharField(max_length=100, blank=True, null=True)
    tags = models.ManyToManyField(Tag, related_name='articles', blank=True)
    explanation = models.TextField(blank=True, null=True)
    published = models.DateTimeField(null=True, blank=True)
