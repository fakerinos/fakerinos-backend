from django.dispatch import receiver
from .signals import game_ended, game_started, player_joined_room, player_left_room
from accounts.models import Player
from .models import GameResult, Room
import logging


@receiver(game_started)
def handle_game_started(sender, **kwargs):
    room = kwargs['room']
    deck = kwargs['deck']
    logging.info(f"Game started: room {room.pk}, deck {deck.pk}")


@receiver(game_ended)
def create_game_results(sender, **kwargs):
    room = kwargs['room']
    deck = kwargs['deck']
    player_scores: dict = kwargs['player_scores']
    logging.info(f"Game ended: room {room.pk}, deck {deck.pk}")

    game_result = GameResult.create(room.players.all(), deck, player_scores)

    players_in_room = room.players.count()
    for player_pk, score in player_scores.items():
        player = Player.objects.get(pk=player_pk)
        room.players.remove(player)
        player.save()
        players_in_room -= 1
        if players_in_room <= 0:
            room.delete()


@receiver(game_ended)
def update_player_metrics(sender, **kwargs):
    player_scores: dict = kwargs['player_scores']

    # Update player scores
    for player_pk, score in player_scores.items():
        player = Player.objects.get(pk=player_pk)
        player.score += score
        player.save()

    # TODO: update player skill rating

    # Sort all players by score (or some other metric) in DESCENDING ORDER and assign ranks
    # TODO: improve efficiency
    for i, player in enumerate(get_sorted_players()):
        logging.error(f"score {player.score} rank {i}")
        player.rank = i + 1
        player.save()


def get_sorted_players():
    return Player.objects.order_by('-skill_rating', '-score')


@receiver(game_ended)
def mark_deck_finished(sender, **kwargs):
    deck = kwargs['deck']
    player_scores: dict = kwargs['player_scores']
    for player_pk, score in player_scores.items():
        player = Player.objects.get(pk=player_pk)
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
