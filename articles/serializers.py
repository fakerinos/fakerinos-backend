from rest_framework import serializers
from .models import Article, Deck, Tag, Domain, DomainTag


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
            'is_poll',
            'url',
            'url_hash',
            'rating',
            'domain',
            'text',
            'thumbnail_url',
            'author',
            'tags',
            'explanation',
            'published',
            'average_score',
            'weighted_average_score',
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
            'title',
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
            'description',
            'thumbnail_url',
        )


class DomainSerializer(serializers.ModelSerializer):
    domain_tags = serializers.SlugRelatedField(many=True, slug_field='name', queryset=DomainTag.objects.all())

    class Meta:
        model = Domain
        fields = (
            'url',
            'url_hash',
            'credibility',
            'rating',
            'domain_tags',
        )


class DomainTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = DomainTag
        fields = (
            'name',
            'description',
            'link',
        )
