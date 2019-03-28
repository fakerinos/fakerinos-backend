from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status
from .serializers import RoomSerializer
from .models import Room


class RoomViewSet(viewsets.ReadOnlyModelViewSet, mixins.CreateModelMixin):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = (permissions.DjangoModelPermissions,)

    def create(self, request, *args, **kwargs):
        # Reject request if user is currently in a room
        user = request.user
        if user.room:
            return Response({
                'detail': 'Cannot create room because you are already in one.'.format(user.room.pk),
                'room': user.room.id,
            },
                status=status.HTTP_400_BAD_REQUEST)

        # Delete currently hosted room if empty (can happen if the user never joins a room they created)
        hosted_room = request.user.hosted_room
        if hosted_room is not None:
            hosted_room.delete_if_empty()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        room = serializer.save()
        user.hosted_room = room
        user.save()
        return Response({'room': room.id}, status=status.HTTP_201_CREATED)
