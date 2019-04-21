from django.db.models import signals
from django.contrib.auth import get_user_model
from rooms.signals import game_ended
from accounts.models import Player
from .models import LeaderBoardStaleMarker
import logging

User = get_user_model()


def mark_leaderboards_stale(sender, **kwargs):
    if 'created' in kwargs and not kwargs['created']:
        return
    logging.info("Invalidating Leaderboard Caches")
    LeaderBoardStaleMarker.objects.all().update(fresh=False)


signals.post_save.connect(mark_leaderboards_stale, sender=Player)
signals.post_save.connect(mark_leaderboards_stale, sender=User)
game_ended.connect(mark_leaderboards_stale)
