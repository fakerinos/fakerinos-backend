from django.apps import AppConfig


class RoomsConfig(AppConfig):
    name = 'rooms'

    def ready(self):
        super(RoomsConfig, self).ready()
        from . import receivers
