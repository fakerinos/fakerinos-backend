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
            'pk',
            'headline',
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
    tags = serializers.SerializerMethodField()

    def get_tags(self, obj):
        return obj.tags

    class Meta:
        model = Deck
        fields = (
            'pk',
            'subject',
            'articles',
            'tags',
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'pk',
            'name',
        )
