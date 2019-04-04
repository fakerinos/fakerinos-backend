from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Profile, Player
from articles.models import Tag, Deck

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'pk',
            'username'
        )


class PlayerSerializer(serializers.ModelSerializer):
    pk = serializers.PrimaryKeyRelatedField(read_only=True)
    room = serializers.PrimaryKeyRelatedField(read_only=True, default=None)
    hosted_room = serializers.PrimaryKeyRelatedField(read_only=True, default=None)

    class Meta:
        model = Player
        fields = (
            'pk',
            'room',
            'hosted_room',
            'skill_rating',
        )


class ProfileSerializer(serializers.ModelSerializer):
    pk = serializers.PrimaryKeyRelatedField(read_only=True)
    interests = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    starred_decks = serializers.PrimaryKeyRelatedField(queryset=Deck.objects.all(), many=True)
    education = serializers.ChoiceField(Profile.EDUCATION_CHOICES)
    gender = serializers.ChoiceField(Profile.GENDER_CHOICES)
    is_complete = serializers.BooleanField(read_only=True)
    age = serializers.IntegerField(allow_null=True, read_only=True)

    class Meta:
        model = Profile
        fields = (
            'pk',
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
