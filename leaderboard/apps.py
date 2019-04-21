from django.apps import AppConfig


class LeaderboardConfig(AppConfig):
    name = 'leaderboard'

    def ready(self):
        super(LeaderboardConfig, self).ready()
        from . import receivers
