from rest_framework import serializers
from articles.models import Deck, Tag
from .models import Room, GameResult
import logging


class RoomSerializer(serializers.ModelSerializer):
    players = serializers.SerializerMethodField()
    deck = serializers.PrimaryKeyRelatedField(queryset=Deck.objects.all())
    tag = serializers.PrimaryKeyRelatedField(read_only=True)

    def get_players(self, obj):
        return [player.user.username for player in obj.players.all()]

    class Meta:
        model = Room
        fields = (
            'pk',
            'max_players',
            'status',
            'players',
            # 'host',
            'subject',
            'deck',
            'tag',
        )
        read_only_fields = (
            'max_players',
            'status',
            'players',
            # 'host',
            'subject',
            'tag',
        )


class FinishSerializer(serializers.Serializer):
    score = serializers.IntegerField(required=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class GameResultSerializer(serializers.ModelSerializer):
    player = serializers.RelatedField(read_only=True, source='user.username')
    deck = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = GameResult
        fields = (
            'deck',
            'player',
            'score',
            'time'
        )
        read_only_fields = (
            'score',
            'deck',
            'player',
        )
