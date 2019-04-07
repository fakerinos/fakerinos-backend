from rest_framework import viewsets
from rest_framework.viewsets import mixins
from rest_framework import permissions
from .models import Profile, Player
from django.contrib.auth import get_user_model
from fakerinos.permissions import ObjectOnlyPermissions
from .serializers import UserSerializer, PlayerSerializer, ProfileSerializer

User = get_user_model()


class UserViewSet(viewsets.ReadOnlyModelViewSet, ):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'username'


class ProfileViewSet(viewsets.ReadOnlyModelViewSet,
                     mixins.UpdateModelMixin, ):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (ObjectOnlyPermissions,)
    lookup_field = 'user__username'


class PlayerViewSet(viewsets.ReadOnlyModelViewSet, ):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = (ObjectOnlyPermissions,)
    lookup_field = 'user__username'
