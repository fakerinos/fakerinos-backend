from rest_framework import serializers
from .models import Room


class RoomSerializer(serializers.ModelSerializer):
    # TODO: make `players` a HyperlinkedRelatedField using the `profile-detail` view.

    class Meta:
        model = Room
        fields = (
            'id',
            'max_players',
            'status',
            'players',
        )
        read_only_fields = (
            'players',
        )
