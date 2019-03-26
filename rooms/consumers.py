from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync
from .models import Room
import logging


class RoomConsumer(JsonWebsocketConsumer):
    def websocket_connect(self, message):
        self.room_id = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'room_%s' % self.room_id
        room = Room.objects.get(id=self.room_id)
        user = self.scope['user']
        players = room.players.all()
        if user.is_authenticated and user.profile not in players and len(players) < room.max_players:
            logging.info("User {} joined room {}".format(self.scope['user'].id, room.id))
            user.profile.room = room
            user.profile.save()
            self.accept()
        elif user.profile in players:
            self.accept()
        else:
            self.close()

    def disconnect(self, code):
        user = self.scope['user']
        if user.is_authenticated:
            room = Room.objects.get(id=user.profile.room.id)
            user.profile.room = None
            user.profile.save()
            logging.info("User {} left room {}".format(user.id, room.id))
            room.delete_if_empty()
