from rest_framework import serializers
from .models import Article


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = (
            'id',
            'headline',
            'rating',
            'text',
            'thumbnail_url',
            'author',
            'tags',
            'explanation',
            'publish_date',
            'upload_date'
        )

    # def create(self, validated_data):
    #     return Article.objects.create(**validated_data)
    #
    # def update(self, instance, validated_data):
    #     instance.headline = validated_data.get('headline', instance.headline)
    #     instance.rating = validated_data.get('rating', instance.rating)
    #     instance.text_url = validated_data.get('text_url', instance.text_url)
    #     instance.thumbnail_url = validated_data.get('thumbnail_url', instance.thumbnail_url)
    #     instance.author = validated_data.get('author', instance.author)
    #     instance.tags = validated_data.get('tags', instance.tags)
    #     instance.explanation = validated_data.get('explanation', instance.explanation)
    #     instance.publish_date = validated_data.get('publish_date', instance.publish_date)
    #     instance.save()
    #     return instance
