from django.db import models
import logging


class Room(models.Model):
    max_players = models.IntegerField(default=4, editable=False)
    status = models.CharField(max_length=128, default='NEW', editable=False)
    subject = models.CharField(max_length=50, unique=True)

    # has a players relation in the User model
    # has a host relation in the User model

    def delete_if_empty(self):
        if self.is_empty():
            logging.info("Room {} is empty. Deleting...".format(self.pk))
            self.delete()

    def is_empty(self):
        return not self.players.exists()
