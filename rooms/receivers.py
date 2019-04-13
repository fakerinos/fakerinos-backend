from django.dispatch import receiver
from .signals import game_ended, game_started, player_joined_room, player_left_room
from .serializers import GameResultSerializer
from accounts.models import Player
from .models import GameResult
import logging


@receiver(game_started)
def handle_game_started(sender, **kwargs):
    room = kwargs['room']
    deck = kwargs['deck']
    logging.info(f"Game started: room {room.pk}, deck {deck.pk}")


@receiver(game_ended)
def create_game_results(sender, **kwargs):
    room = kwargs['room']
    game_uid = kwargs['game_uid']
    deck = kwargs['deck']
    scores = kwargs['scores']
    logging.info(f"Game {game_uid} ended: room {room.pk}, deck {deck.pk}")

    results = []
    for player, score in scores:
        game_result = GameResult.objects.create(score=score, player=player, deck=deck, game_uid=game_uid)
        game_result_serializer = GameResultSerializer(game_result)
        result = game_result_serializer.data
        if len(room.players.all()) == 1:
            room.delete()
        player.room = None
        player.save()
        results.append(result)

    return results


@receiver(game_ended)
def update_player_metrics(sender, **kwargs):
    scores = kwargs['scores']

    # Update player scores
    for player, score in scores:
        player.score += score
        player.save()

    # Sort all players by score (or some other metric) in DESCENDING ORDER and assign ranks
    # TODO: improve efficiency
    players = get_sorted_players()
    for i, player in enumerate(players):
        logging.error(f"score {player.score} rank {i}")
        player.rank = i + 1
        player.save()


def get_sorted_players():
    return Player.objects.order_by('-skill_rating', '-score')


@receiver(game_ended)
def mark_deck_finished(sender, **kwargs):
    deck = kwargs['deck']
    scores = kwargs['scores']
    for player, score in scores:
        player.finished_decks.add(deck)
        player.save()


@receiver(player_left_room)
def handle_player_left(sender, **kwargs):
    room = kwargs['room']
    player = kwargs['player']
    logging.info(f"Player {player.user.username} left room {room.pk}")


@receiver(player_joined_room)
def handle_player_joined(sender, **kwargs):
    room = kwargs['room']
    player = kwargs['player']
    logging.info(f"Player {player.user.username} joined room {room.pk}")
