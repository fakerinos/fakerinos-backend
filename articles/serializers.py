from rest_framework import serializers
from .models import Article, Deck


class ArticleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        fields = (
            'id',
            'headline',
            'rating',
            'domain',
            'text',
            'thumbnail_url',
            'author',
            'tags',
            'explanation',
            'published',
            'created',
            'modified',
        )


class DeckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deck
        fields = (
            'subject',
            'articles',
        )
