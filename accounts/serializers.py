from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Profile, Player
from articles.models import Tag

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'pk',
        )


class PlayerSerializer(serializers.ModelSerializer):
    pk = serializers.PrimaryKeyRelatedField(read_only=True)
    room = serializers.PrimaryKeyRelatedField(read_only=True, default=None)
    hosted_room = serializers.PrimaryKeyRelatedField(read_only=True, default=None)

    class Meta:
        model = Player
        fields = (
            'pk',
            'score',
            'room',
            'hosted_room',
        )


class ProfileSerializer(serializers.ModelSerializer):
    pk = serializers.PrimaryKeyRelatedField(read_only=True)
    interests = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all())
    education = serializers.ChoiceField(Profile.EDUCATION_CHOICES)
    is_complete = serializers.BooleanField()

    class Meta:
        model = Profile
        fields = (
            'pk',
            'interests',
            'education',
            'is_complete'
        )
