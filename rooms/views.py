from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from .models import Room
from .serializers import RoomSerializer


class ArticleViewSet(ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = (permissions.IsAuthenticated,)
