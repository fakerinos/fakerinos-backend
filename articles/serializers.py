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
    stars = serializers.SerializerMethodField()
    times_played = serializers.SerializerMethodField()

    def get_stars(self, obj):
        return obj.starrers.count()

    def get_times_played(self, obj):
        return obj.finishers.count()

    class Meta:
        model = Deck
        fields = (
            'pk',
            'subject',
            'articles',
            'tags',
            'description',
            'thumbnail_url',
            'stars',
            'times_played',
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'name',
        )
