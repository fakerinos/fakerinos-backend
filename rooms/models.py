from django.db import models
from django.contrib.auth import get_user_model


class Room(models.Model):
    pass
    # max_players = models.IntegerField(default=4)
    # num_players = models.IntegerField()
    # created = models.DateTimeField()
    # players = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING, blank=True)
    # status = models.CharField(max_length=128, default='EMPTY')
