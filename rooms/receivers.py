from django.dispatch import receiver
from .signals import game_ended, game_started, player_joined_room, player_left_room
from .serializers import GameResultSerializer
from .models import GameResult
import logging


@receiver(game_started)
def handle_game_started(sender, **kwargs):
    room = kwargs['room']
    deck = kwargs['deck']
    logging.debug(f"Game started: room {room.pk}, deck {deck.pk}")


@receiver(game_ended)
def handle_game_ended(sender, **kwargs):
    room = kwargs['room']
    game_uid = kwargs['game_uid']
    deck = kwargs['deck']
    logging.debug(f"Game {game_uid} ended: room {room.pk}, deck {deck.pk}")
    scores = kwargs['scores']

    datas = []
    for player, score in scores:
        game_result = GameResult.objects.create(score=score, player=player, deck=deck, game_uid=game_uid)
        game_result_serializer = GameResultSerializer(game_result)
        data = game_result_serializer.data
        if len(room.players.all()) == 1:
            room.delete()
        player.room = None
        player.save()
        datas.append(data)

    return datas


@receiver(player_left_room)
def handle_player_left(sender, **kwargs):
    room = kwargs['room']
    player = kwargs['player']
    logging.debug(f"Player {player.user.username} left room {room.pk}")


@receiver(player_joined_room)
def handle_player_joined(sender, **kwargs):
    room = kwargs['room']
    player = kwargs['player']
    logging.debug(f"Player {player.user.username} joined room {room.pk}")
