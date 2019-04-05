from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=50)


class Article(models.Model):
    headline = models.CharField(max_length=500)
    text = models.TextField(blank=True)
    truth_value = models.BooleanField(null=True, blank=True)
    rating = models.CharField(max_length=50, blank=True)
    domain = models.URLField(blank=True)
    url = models.URLField(max_length=500, blank=True)
    thumbnail_url = models.URLField(max_length=500, blank=True)
    author = models.CharField(max_length=100, blank=True)
    tags = models.ManyToManyField(Tag, related_name='articles', blank=True)
    explanation = models.TextField(blank=True)
    published = models.DateTimeField(null=True, blank=True)


class Deck(models.Model):
    subject = models.CharField(max_length=50)
    articles = models.ManyToManyField(Article, related_name='decks')
    description = models.CharField(max_length=200, blank=True)
    thumbnail_url = models.URLField(max_length=500, blank=True)

    # Has a 'starrers' M2M relation in accounts.profile

    @property
    def tags(self):
        if self.articles.exists():
            tags = [article.tags.all() for article in self.articles.all()]
            tags = tags[0].union(*tags[1:])
            return [tag.pk for tag in tags]
        return []
