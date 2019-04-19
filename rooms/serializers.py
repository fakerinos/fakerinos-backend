from rest_framework import serializers
from articles.models import Deck, Tag
from .models import Room, GameResult
import logging


class RoomSerializer(serializers.ModelSerializer):
    players = serializers.SerializerMethodField()
    deck = serializers.PrimaryKeyRelatedField(queryset=Deck.objects.all())

    def get_players(self, obj):
        return [player.user.username for player in obj.players.all()]

    class Meta:
        model = Room
        fields = (
            'pk',
            'max_players',
            'status',
            'players',
            'deck',
            'article_counter',
        )
        read_only_fields = (
            'max_players',
            'status',
            'players',
        )


class FinishSerializer(serializers.Serializer):
    score = serializers.IntegerField(required=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
