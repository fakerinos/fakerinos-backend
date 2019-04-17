from django.db import models


class LeaderBoardStaleMarker(models.Model):
    """
    A table to indicate whether the leaderboard for a given interval is fresh or stale.
    """
    delta = models.DurationField(unique=True, null=True)
    fresh = models.BooleanField(default=False)
