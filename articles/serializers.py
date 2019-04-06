from rest_framework import serializers
from .models import Article, Deck, Tag


class ArticleSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        slug_field='name',
    )

    class Meta:
        model = Article
        fields = (
            'pk',
            'headline',
            'truth_value',
            'url',
            'rating',
            'domain',
            'text',
            'thumbnail_url',
            'author',
            'tags',
            'explanation',
            'published',
        )


class DeckSerializer(serializers.ModelSerializer):
    articles = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Article.objects.all()
    )
    tags = serializers.SlugRelatedField(slug_field='name', many=True, read_only=True)

    class Meta:
        model = Deck
        fields = (
            'pk',
            'subject',
            'articles',
            'tags',
            'description',
            'thumbnail_url',
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'name',
        )
