from django.db.models import signals
from django.contrib.auth import get_user_model
from rooms.signals import game_ended
from accounts.models import Player
from .models import LeaderBoardStaleMarker

User = get_user_model()


def mark_leaderboards_stale(sender, **kwargs):
    if 'created' in kwargs and not kwargs['created']:
        return
    LeaderBoardStaleMarker.objects.all().update(fresh=False)


signals.post_save(mark_leaderboards_stale, sender=Player)
signals.post_save(mark_leaderboards_stale, sender=User)
game_ended.connect(mark_leaderboards_stale)
