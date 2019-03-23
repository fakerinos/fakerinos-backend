from rest_framework import serializers
from .models import Room


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = (
            'id',
            'max_players',
            'num_players',
            'players',
            'created',
            'status',
        )
