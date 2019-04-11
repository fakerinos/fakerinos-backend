from rest_framework import serializers
from .models import Room


class RoomSerializer(serializers.ModelSerializer):
    host = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Room
        fields = (
            'pk',
            'max_players',
            'status',
            'players',
            'host',
            'subject',
        )
        read_only_fields = (
            'players',
            'subject',
        )
