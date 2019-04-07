from channels.generic.websocket import JsonWebsocketConsumer, WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import Room
from articles.models import Deck
import logging
from articles.models import Article
import json
import channels.layers
import websockets
from django.core import serializers

class RoomConsumer(JsonWebsocketConsumer):
    def websocket_connect(self, message):
        self.room_id = self.scope['url_route']['kwargs']['room_name']
        self.deck_id = self.scope['url_route']['kwargs']['deck_name']
        logging.info(self.deck_id)
        self.room_group_name = 'room_%s' % self.room_id
        # Room.objects.create(pk=1)
        # Article.objects.create(headline="test1")
        # Article.objects.create(headline="test2")
        # room = Room.objects.get(pk=1)
        # async_to_sync(channels.layers.get_channel_layer(alias="game-consumer").send(
        #     "game-consumer",
        #     {
        #         "type": 'websocket.connect'
        #     },
        # ))
        room = Room.objects.get(id=self.room_id)
        user = self.scope['user']
        players = room.players.all()
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        if user.is_authenticated and user.profile not in players and len(players) < room.max_players:
            self.accept()
            logging.info("User {} joined room {}".format(self.scope['user'].id, room.id))
            user.player.room = room
            user.player.save()
            self.deck = None
            logging.info(self.deck_id)
            # if Deck.objects.filter(pk=self.deck_id):
            #     logging.info(self.deck_id)
            #     logging.info("hey")
            #     self.deck = serializers.serialize("json", [Deck.objects.get(pk=self.deck_id).articles])
            # async_to_sync(self.send(text_data=json.dumps({
            #     'message': self.deck
            # })))

        elif user.profile in players:
            self.accept()
            self.deck = None
            if Deck.objects.filter(pk=self.deck_id):
                self.deck = serializers.serialize("json", [Deck.objects.get(pk=self.deck_id).articles])
            self.send({
                'message': self.deck
            })
        else:
            self.close()

    def disconnect(self, code):
        user = self.scope['user']
        if user.is_authenticated:
            room = Room.objects.get(id=user.player.room.pk)
            user.player.room = None
            user.save()
            logging.info("User {} left room {}".format(user.pk, room.pk))
            room.delete_if_empty()

    def receive_json(self, content, **kwargs):
        # MUST BE double quotes !!! ""
        user = self.scope['user']
        message = content["message"]
        cont = json.loads(message)
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            cont
        )

    def article_request(self, event):
        article_pk = event["input"]
        if Article.objects.filter(pk=article_pk).exists():
            article = serializers.serialize("json", [Article.objects.get(pk=article_pk)])
        else:
            article = None
        self.send(text_data=json.dumps({
            'message': article
        }))

    def update_score(self):
        user = self.scope['user']
        #TODO update score

    def submit_final_score(self):
        user = self.scope['user']


class GameConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        async_to_sync(self.channel_layer.group_add)(
            "gameconsumer",
            self.channel_name
        )

    def websocket_connect(self, message):
        """self.game_group_name = 'game_%s'"""
        self.accept()

    def websocket_disconnect(self, message):
        """
        # async_to_sync(self.channel_layer.send(
        #
        # ))"""