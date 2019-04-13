from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Profile, Player
from articles.serializers import DeckSerializer
from articles.models import Tag, Deck

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
        )


class PlayerSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(read_only=True, slug_field='username')
    room = serializers.PrimaryKeyRelatedField(read_only=True, default=None)
    games = serializers.SerializerMethodField()

    def get_games(self, obj):
        games = obj.games.all()
        return [{'deck': game.deck.pk, 'score': game.score, 'time': str(game.time)} for game in games]

    class Meta:
        model = Player
        fields = (
            'user',
            'room',
            'skill_rating',
            'games'
        )


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(read_only=True, slug_field='username')
    interests = serializers.SlugRelatedField(queryset=Tag.objects.all(), many=True, slug_field='name')
    starred_decks = serializers.PrimaryKeyRelatedField(queryset=Deck.objects.all(), many=True)
    is_complete = serializers.BooleanField(read_only=True)
    age = serializers.IntegerField(allow_null=True, read_only=True)

    class Meta:
        model = Profile
        fields = (
            'user',
            'interests',
            'education',
            'is_complete',
            'age',
            'gender',
            'birth_date',
            'name',
            'avatar',
            'starred_decks',
            'onboarded',
        )
