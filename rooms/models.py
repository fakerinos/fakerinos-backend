from django.db import models
import logging


class Room(models.Model):
    max_players = models.IntegerField(default=4, editable=False)
    status = models.CharField(max_length=128, default='NEW', editable=False, blank=True)
    subject = models.CharField(max_length=50, unique=True, editable=False, null=True, blank=True)
    deck = models.OneToOneField('articles.Deck', on_delete=models.PROTECT, null=True)

    # has a players relation in the Player model

    def delete_if_empty(self):
        if self.is_empty():
            logging.info(f"Room {self.pk} is empty. Deleting...")
            self.delete()
        else:
            logging.info(f"Room {self.pk} is not empty. Won't delete.")

    def is_empty(self):
        return not self.players.exists()


class GameResult(models.Model):
    """
    Create one per player per game.
    `game_uid` field must be unique for each game.
    This serves to group `GameResult`s that belong to the same game session.
    """
    game_uid = models.UUIDField(null=True)  # must be provided at creation time
    player = models.ForeignKey('accounts.Player', related_name='games', editable=False, on_delete=models.CASCADE)
    deck = models.ForeignKey('articles.Deck', on_delete=models.SET_NULL, editable=False, null=True)
    time = models.DateTimeField(auto_now_add=True, blank=True, null=True, editable=False)
    score = models.IntegerField(editable=False, null=True)

    @property
    def game_results(self):
        return GameResult.objects.filter(game_uid=self.game_uid)
