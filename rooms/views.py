from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status
from .serializers import RoomSerializer, FinishSerializer, GameResultSerializer
from .models import Room, GameResult
from . import exceptions
from . import signals
from accounts.models import Player
from articles.models import Article, Deck
from articles.serializers import DeckSerializer
import random


class SinglePlayer(viewsets.ReadOnlyModelViewSet, mixins.CreateModelMixin):
    """
    A ViewSet to handle the basic single-player game mode.
    Create a room by providing a deck ID.
    Finish the game by POSTing to `end-game` with the final score.
    """
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    http_method_names = ['get', 'post', 'head', 'options']

    def create(self, request, *args, **kwargs):
        room_serializer = self.get_serializer(data=request.data)

        # Reject request if deck cannot be found (or on other serializer errors)
        room_serializer.is_valid(raise_exception=True)
        data = room_serializer.validated_data
        deck = data['deck']

        # Reject request if user is currently in a room
        player = request.user.player
        if player.room:
            raise exceptions.AlreadyInRoomException(
                'Cannot create room because you are already in room {}.'.format(player.room.id)
            )

        # If player is already in a room, remove them from it
        player_room = player.room
        player.room = None
        if player_room:
            player_room.delete_if_empty()
        player.save()

        # Create single player room, set the deck, send the `game_started` signal
        room = room_serializer.save()
        room.max_players = 1
        room.deck = deck
        room.save()
        signals.game_started.send(self.__class__, deck=deck, room=room)

        # Add player to room, send `player_joined_room` signal
        player.room = room
        player.save()
        signals.player_joined_room.send(self.__class__, room=room, player=player)

        # Return deck information
        deck_serializer = DeckSerializer(deck)

        return Response(deck_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def finish(self, request):
        """
        Finish the game and delete the room if it's empty. Use only for single player.
        Send a `score` parameter.
        """
        finish_serializer = FinishSerializer(data=request.data)
        finish_serializer.is_valid(raise_exception=True)
        request_data = finish_serializer.data
        user = request.user
        player = user.player
        room = player.room
        if room is None:
            raise exceptions.NotInRoomException()
        deck = room.deck
        score = request_data['score']
        signals.game_ended.send(self.__class__, room=room, deck=deck, player_scores={player.pk: score})
        room.delete()
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def leave(self, request, *args, **kwargs):
        player = request.user.player
        room = player.room
        if room is None:
            raise exceptions.NotInRoomException()
        if len(room.players.all()) == 1:
            room.delete()
        player.room = None
        player.save()
        return Response(status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False)
    def fake_a_game(self, request, *args, **kwargs):
        player = Player.objects.order_by('?').first()
        deck = Deck.objects.order_by('?').first()
        score = random.randint(0, 100 * len(deck.articles.all()))
        room = Room.objects.create(deck=deck, max_players=1)
        room.players.add(player)
        signals.game_ended.send(self.__class__, room=room, deck=deck, player_scores={player.pk: score})
        room.delete()
        return Response(status=status.HTTP_201_CREATED)


class GameResultViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = GameResultSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.request.user.player.games.all()
