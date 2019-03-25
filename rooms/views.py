from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status
from .serializers import RoomSerializer
from .models import Room


class RoomViewSet(viewsets.ReadOnlyModelViewSet, mixins.CreateModelMixin):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = (permissions.IsAuthenticated, permissions.DjangoModelPermissions)

    def create(self, request, *args, **kwargs):
        profile = request.user.profile
        if profile.room:
            return Response({'detail': 'You are already in room {}.'.format(profile.room.id)},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        room = serializer.save()
        profile.room = room
        profile.save()
        return Response({'room': room.id}, status=status.HTTP_201_CREATED)
