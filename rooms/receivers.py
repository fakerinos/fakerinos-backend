from django.dispatch import receiver
from .signals import game_ended, game_started, player_joined_room, player_left_room, article_swiped
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


@receiver(game_ended)
def update_player_metrics(sender, **kwargs):
    room = kwargs['room']
    deck = kwargs['deck']
    players = room.players.all()
    player_scores: dict = kwargs['player_scores']

    # Update player scores
    for player_pk, score in player_scores.items():
        player = Player.objects.get(pk=player_pk)
        player.score += score
        player.save()

    # Update player skill rating
    if len(players) == 1:  # single player
        player = players.first()
        score = player_scores[player.pk]
        reward = get_single_player_sr_update(player, score, deck, base_reward=50)
        logging.info(f"Score = {score}")
        logging.info(f"SR += {reward}")
        player.skill_rating += reward
        player.save()
    elif len(players) > 1:  # multiplayer
        rewards = get_multiplayer_sr_updates(players, player_scores, deck, base_reward=50)
        for player, reward in rewards:
            player.skill_rating += reward
            player.save()
    else:
        raise ValueError("Room has < 1 players. wut.")

    # Sort all players by score (or some other metric) in DESCENDING ORDER and assign ranks
    # TODO: improve efficiency
    for i, player in enumerate(get_sorted_players()):
        player.rank = i + 1
        player.save()


def get_multiplayer_sr_updates(players, player_scores, deck, base_reward):
    return [get_single_player_sr_update(player,
                                        player_scores[player.pk],
                                        deck,
                                        base_reward=base_reward) for player in players]


def get_single_player_sr_update(player, score, deck, base_reward=50):
    if deck.articles.count() == 0:
        return 0
    current_sr = player.skill_rating
    sr_ratio = (current_sr - 500) / 1000
    score_ratio = (score / (100 * deck.articles.count())) - 0.5  # -0.5 - 0.5
    reward = base_reward * ((1.2 * score_ratio) - (0.8 * sr_ratio))
    if reward + current_sr > 1000:
        reward = 1000 - current_sr
    elif reward + current_sr < 0:
        reward = -current_sr
    return reward


def get_sorted_players():
    return Player.objects.order_by('-skill_rating', '-score')


@receiver(game_ended)
def mark_deck_finished(sender, **kwargs):
    deck = kwargs['deck']
    player_scores: dict = kwargs['player_scores']
    room = kwargs['room']
    players = room.players.all()
    for player in players:
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


@receiver(article_swiped)
def add_swiper_to_article(sender, **kwargs):
    logging.info("Swiper no swiping")
    player = kwargs['player']
    article = kwargs['article']
    outcome = kwargs['outcome']
    if outcome:
        article.true_swipers.add(player)
    else:
        article.false_swipers.add(player)
    article.save()
