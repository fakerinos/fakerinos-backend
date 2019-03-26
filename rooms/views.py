from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status
from .serializers import RoomSerializer
from .models import Room
import logging


class RoomViewSet(viewsets.ReadOnlyModelViewSet, mixins.CreateModelMixin):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        # Reject request if user is currently in a room
        profile = request.user.profile
        if profile.room:
            return Response({
                'detail': 'Cannot create room because you are already in one.'.format(profile.room.id),
                'room': profile.room.id,
            },
                status=status.HTTP_400_BAD_REQUEST)

        # Delete all empty rooms that the requesting user has previously created
        user_rooms = request.user.room_creator.all() | Room.objects.filter(creator=None)
        if user_rooms.exists():  # If user has created at least one room that still exists
            for room in user_rooms.all():
                room.delete_if_empty()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        room = serializer.save(creator=request.user)
        return Response({'room': room.id}, status=status.HTTP_201_CREATED)
