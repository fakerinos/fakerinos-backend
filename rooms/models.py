from django.db import models
from django.dispatch import receiver
from . import signals
import logging
from accounts.models import Player
import json


class Room(models.Model):
    max_players = models.IntegerField(default=2, editable=False)
    status = models.CharField(max_length=128, default='NEW', editable=False, blank=True)
    subject = models.CharField(max_length=50, unique=True, editable=False, null=True, blank=True)
    tag = models.OneToOneField('articles.Tag', on_delete=models.PROTECT, null=True, blank=True)
    deck = models.OneToOneField('articles.Deck', on_delete=models.PROTECT, null=True)
    article_counter = models.IntegerField(default=0)

    def delete_if_empty(self):
        if self.is_empty():
            logging.info(f"Room {self.pk} is empty. Deleting...")
            self.delete()
        else:
            logging.info(f"Room {self.pk} is not empty. Won't delete.")
            logging.info("Some players are still in the room: "+ str(self.players.all()))

    def is_empty(self):
        return not self.players.exists()

    def force_delete(self):
        if len(self.players.all()) == 1:
            self.players.set(Player.objects.filter(pk=0))
            self.delete_if_empty()


class GameResult(models.Model):
    game_uid = models.UUIDField(null=True)  # must be provided at creation time
    time = models.DateTimeField(auto_now_add=True, blank=True, null=True, editable=False)
    player = models.ForeignKey('accounts.Player', related_name='games', editable=False, on_delete=models.CASCADE)
    deck = models.ForeignKey('articles.Deck', on_delete=models.SET_NULL, editable=False, null=True)
    score = models.IntegerField(editable=False)

    @property
    def all_player_results(self):
        return GameResult.objects.filter(game_uid=self.game_uid)
