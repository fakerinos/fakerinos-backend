from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status
from .serializers import RoomSerializer
from .models import Room
from .exceptions import AlreadyInRoomException
import logging
from articles.models import Article, Deck
import json
from django.core import serializers


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
        logging.error(request.data)

        data = []
        if "subject" in request.data and Deck.objects.filter(subject=request.data["subject"]).exists():
            deck_subject = request.data["subject"]
            deck_id = Deck.objects.get(subject=deck_subject).pk
            article_list = Deck.objects.get(pk=deck_id).articles.values_list('pk', flat=True)
            for id in article_list:
                data.append(id)
            return_value = json.dumps({'article_list': data, 'room': room.id})
            return Response(return_value, status=status.HTTP_201_CREATED)
        else:
            logging.error("deck dont exists")
            return Response(data,status=status.HTTP_404_NOT_FOUND)

    #detail=True means for single object =False means for entire collection
    @action(detail=False, methods=['post'])
    def end(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        #TODO get room from pk in endpoint and close room
        logging.info(request.data["pk"])
        room = self.get_object()
        logging.info(room)
        room.delete(self)
        request.user.player.hosted_room = None

    # @action(detail=False)



