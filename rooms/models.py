from django.db import models
from fakerinos.models import CreatorModel
import logging


class Room(CreatorModel):
    max_players = models.IntegerField(default=4, editable=False)
    status = models.CharField(max_length=128, default='NEW', editable=False)

    # has a players relation in the Profile model

    def delete_if_empty(self):
        if self.is_empty():
            logging.info("Room {} is empty. Deleting...".format(self.id))
            self.delete()

    def is_empty(self):
        return not self.players.exists()
