from django.db import models


# Create your models here.
class Article(models.Model):
    headline = models.CharField(max_length=500)
    rating = models.CharField(max_length=50)
    domain = models.URLField(null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    thumbnail_url = models.URLField(null=True, blank=True)
    author = models.CharField(max_length=100, null=True, blank=True)
    tags = models.CharField(max_length=100, null=True, blank=True)
    explanation = models.TextField(null=True, blank=True)
    publish_date = models.DateField(null=True, blank=True)
    upload_date = models.DateField(auto_now_add=True)
