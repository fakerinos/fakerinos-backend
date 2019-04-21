from django.db import models
import hashlib
import numpy as np


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    thumbnail_url = models.ImageField(blank=True, null=True, upload_to='tag_thumbnails')

    def __str__(self):
        return f"Tag ({self.name})"


class Article(models.Model):
    headline = models.CharField(max_length=500)
    text = models.TextField(blank=True)
    truth_value = models.BooleanField(default=True, blank=True)
    is_poll = models.BooleanField(default=False, blank=True)
    rating = models.CharField(max_length=50, blank=True)
    domain = models.URLField(blank=True)
    url = models.URLField(max_length=1000, blank=True)
    url_hash = models.CharField(max_length=1000, blank=True, editable=False)
    thumbnail_url = models.URLField(max_length=1000, blank=True)
    author = models.CharField(max_length=100, blank=True)
    tags = models.ManyToManyField(Tag, related_name='articles', blank=True)
    explanation = models.TextField(blank=True)
    published = models.DateTimeField(null=True, blank=True)
    true_swipers = models.ManyToManyField('accounts.Player', related_name='true_swiped')
    false_swipers = models.ManyToManyField('accounts.Player', related_name='false_swiped')

    def save(self, *args, **kwargs):
        if self.url is not None:
            self.url_hash = hashlib.md5(self.url.encode('utf8')).hexdigest()
        super(Article, self).save(*args, **kwargs)

    def __str__(self):
        headline_max_len = 40
        headline = f"{self.headline[:headline_max_len]}..." if len(self.headline) > headline_max_len else self.headline
        return f"Article ({headline})"

    @property
    def average_score(self):
        num_true = self.true_swipers.count()
        num_false = self.false_swipers.count()
        if num_true or num_false:
            return num_true / (num_true + num_false)
        else:
            return None

    @property
    def weighted_average_score(self):
        true_swipers = list(self.true_swipers.all())
        false_swipers = list(self.false_swipers.all())
        if true_swipers or false_swipers:
            values = [1 for _ in true_swipers] + [0 for _ in false_swipers]
            weights = [p.skill_rating for p in true_swipers + false_swipers]
            return np.average(values, weights=weights)
        else:
            return None


class Deck(models.Model):
    title = models.CharField(max_length=100, unique=True)
    articles = models.ManyToManyField(Article, related_name='decks')
    description = models.CharField(max_length=200, blank=True)
    thumbnail_url = models.ImageField(null=True, blank=True, upload_to='deck_thumbnails')
    tags = models.ManyToManyField(Tag, related_name='tags', blank=True, editable=False)

    def __str__(self):
        return f"Deck ({self.title})"

    # Has a 'starrers' M2M relation in accounts.profile
    # Has a 'finishers' M2M relation in accounts.profile


class Domain(models.Model):
    url = models.URLField(max_length=100, unique=True)
    url_hash = models.CharField(max_length=100, editable=False, blank=True)
    credibility = models.PositiveSmallIntegerField(default=5, blank=True)
    rating = models.CharField(max_length=100, blank=True)
    domain_tags = models.ManyToManyField('articles.DomainTag', related_name='domains', blank=True)

    def save(self, *args, **kwargs):
        if self.url is not None:
            self.url_hash = hashlib.md5(self.url.encode('utf8')).hexdigest()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Domain ({self.url})"


class DomainTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    link = models.URLField(blank=True)

    def __str__(self):
        return f"DomainTag ({self.name})"
