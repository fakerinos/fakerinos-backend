from django.db import models
from django.core import validators
from accounts.models import Player
import logging
from accounts.models import Player
import json


class Room(models.Model):
    max_players = models.IntegerField(default=2, editable=False)
    status = models.CharField(max_length=128, default='NEW', editable=False, blank=True)
    deck = models.OneToOneField('articles.Deck', on_delete=models.PROTECT, null=True)
    article_counter = models.IntegerField(default=0)

    def __str__(self):
        players = [p.user.username for p in self.players.all()]
        return f"Room | {self.deck} | Players {players} | Status {self.status}"

    def delete_if_empty(self):
        if self.is_empty():
            logging.info(f"Room {self.pk} is empty. Deleting...")
            self.delete()
        else:
            logging.info(f"Room {self.pk} is not empty, {self.players.all()} are still in it. Won't delete.")

    def is_empty(self):
        return not self.players.exists()

    def force_delete(self):
        if len(self.players.all()) == 1:
            self.players.set(Player.objects.filter(pk=0))
            self.delete_if_empty()


def player_scores_to_commasep(player_scores):
    player_pks, scores = zip(*player_scores.items())
    return ','.join(map(str, player_pks)), ','.join(map(str, scores))


class GameResult(models.Model):
    """
    Create one per game.
    USE THE `cls.create()` METHOD TO CREATE THESE OBJECTS, NOT `cls.objects.create()`.
    """
    players = models.ManyToManyField('accounts.Player', related_name='games')
    time = models.DateTimeField(auto_now_add=True, blank=True, null=True, editable=False)
    deck = models.ForeignKey('articles.Deck', on_delete=models.SET_NULL, editable=False, null=True)
    player_pks = models.CharField(max_length=500, validators=[validators.int_list_validator()], default='')
    scores = models.CharField(max_length=500, validators=[validators.int_list_validator()], default='')

    def __str__(self):
        players = [p.user.username for p in self.players.all()]
        return f"GameResult @ {self.time.strftime('%Y-%m-%d %H:%M:%S')} | {self.deck} | Players {players} "

    @classmethod
    def create(cls, players, deck, player_scores, **kwargs):
        game_result = cls.objects.create(deck=deck, **kwargs)
        game_result.player_scores = player_scores
        game_result.save()
        game_result.players.set(players)
        return game_result

    @property
    def player_scores(self) -> dict:
        player_pks = [int(v) for v in self.player_pks.split(',')]
        scores = [int(v) for v in self.scores.split(',')]
        assert len(scores) == len(player_pks), "PLAYER-SCORE LISTS MISMATCH!"
        return dict(zip(player_pks, scores))

    @player_scores.setter
    def player_scores(self, score_dict: dict):
        # TODO: parse {player: score} dict and store it as key-value lists
        self.player_pks, self.scores = player_scores_to_commasep(score_dict)
