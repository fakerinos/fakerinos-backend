from channels.generic.websocket import JsonWebsocketConsumer, WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import Room, GameResult
from articles.models import Deck, Article
import logging
import json
from django.core import serializers
import random
from articles.serializers import ArticleSerializer,DeckSerializer,TagSerializer
from rest_framework.renderers import JSONRenderer
import time
from channels.exceptions import (
    AcceptConnection,
    DenyConnection,
    InvalidChannelLayerError,
    StopConsumer,
)
import asyncio
from . import signals


class RoomConsumer(JsonWebsocketConsumer):
    def websocket_connect(self, message):
        logging.info("\tEntering WS connection handler")
        try:
            self.user = self.scope['user']
        except:
            message = "connection error :: either you are not logged in or cannot provide authentication"
            self.send_json({
                "action": "admin",
                "message": message,
            })
            self.close()
        self.accept()
        self.send_json({
            "action": "admin",
            "message": "connection success"
        })

    def request_to_join(self):
        logging.info("\tEntering request_to_join handler")
        self.room_pk = None
        self.tag = None
        # should not request room when already in room
        if self.user.player.room is not None:
            self.send_json({"action": "admin", "message": "There is something wrong with your connection. Please try again"})
            # self.websocket_disconnect({"code": None})
            self.leave_room()
            self.close()
        try:
            self.deck_pk = self.scope['url_route']['kwargs']['tag']
            self.room_pk = self.scope['url_route']['kwargs']['room_pk']

        except Exception as e:
            logging.exception("find room :: No room name found OR no subject found")

        # quickmatching method
        for room in Room.objects.all():
            if len(room.players.all()) != room.max_players:
                self.join_room(room)
                break
        if self.user.player.room is None:
            self.create_room(self.tag)



    def create_room(self, tag):
        logging.info("\tEntering create_room handler")

        room = Room.objects.create()
        room.save()
        self.user.player.room = room
        self.hosted_room = room
        self.user.player.save()
        if hasattr(self, "deck_pk") and self.deck_pk is not None:
            pass
        else:
            self.choose_random_deck()

        room.deck = Deck.objects.get(pk=self.deck_pk)
        room.save()
        self.room_group_name = 'room_%s' % self.user.player.room.pk

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        # signals.player_joined_room.send(sender=self.__class__, room=room, player=self.user.player)
        self.send_everyone({"action": "admin", "message": "created room %s" % str(room.pk)})
        self.send_everyone({"action": "admin", "message": "created room .. waiting for other players to join"})

    def join_room(self, room_object):
        logging.info("\tEntering join room")
        room = room_object
        if self.user.is_authenticated and self.user.profile not in room.players.all() and len(room.players.all()) < room.max_players:
            logging.info("User {} joined room {}".format(self.scope['user'].id, room.id))
            self.user.player.room = room
            self.user.player.save()
            self.room_group_name = 'room_%s' % room.pk
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )
            #logging.info("joined room")
            # signals.player_joined_room.send(sender=self.__class__, room=room, player=self.user.player)
            self.send_json({"action":"admin", "message": "alloted room %s" % str(room.pk)})
            self.send_everyone({"action": "admin", "message": "User {} has joined the room".format(self.user)})
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                "type": "receive_json",
                "message": {
                    "action": "admin",
                    "schema": "game_ready",
                    }
                }
            )
            # check if game is ready



        elif self.user.profile in room.players.all():
            #TODO how to handle if user already in room --> will that happen lol
            logging.info("Already in room bro")

        elif len(room.players.all()) == room.max_players:
            #logging.info("room full ==> try again")
            #TODO handle if player wants specific room but full
            self.send_json({
                "action": "admin",
                "message": "room is full .. disconnecting from game",
            })
            self.close()

    def leave_room(self):
        logging.info("\tLeaving room")
        user = self.scope['user']
        room = user.player.room
        if user.is_authenticated:
            self.user.player.room.players.remove(self.user.player)
            self.user.save()
            # logging.info("User {} left room {}".format(user.pk, room.pk))
            room.delete_if_empty()
            # signals.player_left_room.send(sender=self.__class__, room=room, player=self.user.player)
        self.close()

    def receive_json(self, content, **kwargs):
        logging.info(".. receiving message from client")
        logging.info(content)
        if "type" in content.keys():
            get_action = content["message"]["action"]
            get_schema = content["message"]["schema"]
            getattr(self, get_action)(get_schema)
        else:
            self.send_json({
                "action": "admin",
                "message": "server received your message"
            })
            # MUST BE double quotes !!! ""
            # handle both string and dict type
            if type(content) is str:
                try:
                    content_message = json.loads(content)
                    get_action = content_message["action"]
                    get_schema = content_message["message"]
                    getattr(self, get_action)(get_schema)
                    logging.info("uh huh")
                except Exception as e:
                    logging.exception(e)

            elif type(content) is dict:
                try:
                    get_action = content["action"]
                    get_schema = content["message"]
                    getattr(self, get_action)(get_schema)
                except Exception as e:
                    logging.exception(e)
            # else:
                #logging.exception("receive json error :: received class type inconsistent, should be str or dict")

    def admin(self, message):
        # only to handle admin messages to self
        logging.info("\tEntering admin handler")
        getattr(self, message)()

    def game_ready(self):
        logging.info("\tEntering game handler")
        # TODO start time and counter
        if hasattr(self, "hosted_room"):
            if self.hosted_room == self.user.player.room and len(self.user.player.room.players.all()) == self.user.player.room.max_players:
                self.send_everyone({
                    "action": "admin",
                    "message": "game is ready",
                })
                # self.next_article()
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        "type": "receive_json",
                        "message": {
                            "action": "admin",
                            "schema": "next_article",
                        }
                    }
                )

    def next_article(self):
        logging.info("\tEntering article handler")
        deck = self.user.player.room.deck
        list_articles = deck.articles.values_list(flat=True)
        article_counter = self.user.player.room.article_counter
        # game end
        if article_counter == len(deck.articles.all()):
            #TODO only host sends signal
            logging.info("GAME ENDED")
            self.user.player.room.article_counter = 0
            self.user.player.room.save()

            list_of_scores = self.get_list_of_scores("id")
            self.send_everyone({
                "action": "game end",
                "message": {
                    "score": list_of_scores,
                }
            })
            #TODO clean up disconnection
            if hasattr(self, "hosted_room"):
                self.send_json({"action": "admin", "message": "lalala"})
                if self.hosted_room.pk == self.user.player.room.pk:
                    signals.game_ended.send_robust(sender=self.__class__, room=self.user.player.room, deck=deck, player_scores=self.get_list_of_scores("pk"))
            #signals.game_started.send(sender=self.__class__, room=self.user.player.room, deck=deck, game_uid=self.user.player.room.pk, scores=list_of_scores)

        else:
            curr_article = Article.objects.get(pk=list_articles[article_counter])
            #logging.info("getting article")
            self.send_json({
                "action": "new card",
                "message": str(JSONRenderer().render(ArticleSerializer(curr_article).data)),
                # "message": serializers.serialize("json", ArticleSerializer(article))
            })

    def check_ready(self, room):
        logging.info("\tChecking if everyone is ready")
        complete_ready = True
        for player in room.players.all():
            if not player.ready:
                complete_ready = player.ready
                break
        if complete_ready:
            self.user.player.room.article_counter += 1
            self.user.player.room.save()
            self.next_article()
        else:
            self.send_json({"action": "admin", "message": "Still waiting for all players to answer"})

    def response(self, message):
        logging.info("\tEntering response handler")
        response = message["response"]
        time_remaining = message["time_remaining"]
        # 0 for false 1 for true
        result = 0
        room = self.user.player.room
        deck = self.user.player.room.deck
        list_articles = deck.articles.values_list(flat=True)
        article_counter = self.user.player.room.article_counter
        curr_article = Article.objects.get(pk=list_articles[article_counter])
        logging.info("LOGGING responses")

        if response == curr_article.truth_value:
            result = 1
        elif response != curr_article.truth_value:
            result = -1
        if hasattr(self.user.player, "score"):
            self.user.player.score += result
        else:
            #logging.info("Something is wrong with player score values")
            self.user.player.score = result

        list_of_scores = self.get_list_of_scores("id")
        self.send_everyone({
            "action": "result",
            "message": {
                "result": result,
                "score": list_of_scores,
                "score_diff": {str(self.user): result}
            }
        })
        self.user.player.ready = True
        self.user.player.save()
        self.check_ready(room)

    def get_list_of_scores(self, id_or_pk):
        logging.info("\tGetting scores")
        room = self.user.player.room
        list_of_scores = {}
        try:
            if id_or_pk == "id":
                for player in room.players.all():
                    list_of_scores[str(player.user)] = player.score
            elif id_or_pk == "pk":
                for player in room.players.all():
                    list_of_scores[player.pk] = player.score

        except Exception as e:
            logging.exception("Error in getting list of player scores")
            #logging.exception(e)
        return list_of_scores

    def send_everyone(self, nested_data):
        # logging.info("\tEntering sending everyone handler")
        if hasattr(self, "room_group_name"):
            try:
                # if nested_data["other_player"] is not None:
                #     for player in self.user.player.room.players:
                #         break
                # else:
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        "type": "send_json",
                        "action": nested_data["action"],
                        "message": nested_data["message"],
                    }
                )
            except Exception as e:
                #logging.exception(e)
                self.send_json({
                    "action": "admin",
                    "message": "Your message was not send out, please try again",
                })
        else:
            self.send_json({
                "action": "admin",
                "message": "Can't send message. You're not in any group yet"
            })

    def choose_random_deck(self):
        number_of_decks = len(Deck.objects.all())
        self.deck_pk = random.randint(1, number_of_decks)
        if Deck.objects.filter(pk=self.deck_pk).exists() and Deck.objects.get(pk=self.deck_pk).articles.all() is not None:
            logging.info("Playing Deck " + str(self.deck_pk))

        else:
            logging.info("Deck empty")
            self.choose_random_deck()

    def wait_for_disconnect(self):
        if self.user.player.room is not None:
            self.wait_for_disconnect()
