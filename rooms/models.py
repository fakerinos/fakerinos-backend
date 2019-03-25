from django.db import models
from fakerinos.models import BaseModel
import logging


class Room(BaseModel):
    max_players = models.IntegerField(default=4, editable=False)
    status = models.CharField(max_length=128, default='NEW', editable=False)

    # has a players relation in the Profile model

    def delete_if_empty(self):
        if self.status != 'NEW' and not self.players.exists():
            self.delete()
            logging.info("Room {} is empty. Deleting...".format(self.id))
