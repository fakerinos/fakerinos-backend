from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status
from .serializers import RoomSerializer
from .models import Room
from .exceptions import AlreadyInRoomException
import logging


class RoomViewSet(viewsets.ReadOnlyModelViewSet, mixins.CreateModelMixin):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    http_method_names = ['get', 'post', 'head', 'options']

    def create(self, request, *args, **kwargs):
        # Reject request if user is currently in a room
        player = request.user.player
        logging.error(str(player.user))
        logging.error(str(player.room))
        if player.room:
            raise AlreadyInRoomException(
                'Cannot create room because you are already in room {}.'.format(player.room.id)
            )
        # Delete currently hosted room if empty (can happen if the user never joins a room they created)
        hosted_room = player.hosted_room
        if hosted_room is not None:
            hosted_room.delete_if_empty()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        room = serializer.save()
        player.hosted_room = room
        player.save()
        Room.objects.create()
        return Response({'room': room.id}, status=status.HTTP_201_CREATED)
