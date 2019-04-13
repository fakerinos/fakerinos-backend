from django.db import models
from django.dispatch import receiver
from . import signals
import logging
from accounts.models import Player

class Room(models.Model):
    max_players = models.IntegerField(default=2, editable=False)
    status = models.CharField(max_length=128, default='NEW', editable=False, blank=True)
    subject = models.CharField(max_length=50, unique=True, editable=False, null=True, blank=True)
    tag = models.OneToOneField('articles.Tag', on_delete=models.PROTECT, null=True, blank=True)
    deck = models.OneToOneField('articles.Deck', on_delete=models.PROTECT, null=True)

    # has a players relation in the Player model

    def delete_if_empty(self):
        if self.is_empty():
            logging.info("Room {} is empty. Deleting...".format(self.pk))
            self.delete()
        else:
            logging.error("models delete_if_empty ::: ROOM NOT EMPTY LA SIAL")
            logging.error("players still in the room: " + str(self.players.all()))

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
