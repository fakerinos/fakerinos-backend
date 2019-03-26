from rest_framework import serializers
from .models import Article, Deck, Tag


class ArticleSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

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
    articles = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Article.objects.all()
    )
    tags = serializers.SerializerMethodField()

    def get_tags(self, obj):
        return obj.tags

    class Meta:
        model = Deck
        fields = (
            'id',
            'subject',
            'articles',
            'tags',
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
        )
