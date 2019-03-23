from rest_framework import serializers
from .models import Article


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
    articles = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='deck-detail'
    )

    class Meta:
        model = Deck
        fields = (
            'subject',
            'articles',
        )
