from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from .models import Room
from .serializers import ProfileSerializer


class ProfileViewSet(ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (permissions.IsAuthenticated, permissions.DjangoObjectPermissions)
