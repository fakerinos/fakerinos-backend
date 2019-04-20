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
        try:
            self.user = self.scope['user']
        except:
            message = "connection error :: either you are not logged in or cannot provide authentication"
            self.send_json({
                "action": "admin",
                "message": message,
            })
            self.close()

        logging.info("\t{} connecting to WS".format(self.user))
        self.accept()
        async_to_sync(self.channel_layer.group_add)(
            "user_{}".format(self.user.player.pk),
            self.channel_name,
        )
        self.send_json({
            "action": "admin",
            "message": "connection success"
        })

    def request_to_join(self):
        logging.info("\t{} requesting to join a room".format(self.user))
        self.room_pk = None
        self.tag = None

        path_dict = self.scope['url_route']['kwargs']
        logging.info(path_dict)
        if "play_mode" in path_dict.keys():
            if path_dict["play_mode"] == "single-player":
                if 'deck_pk' in path_dict.keys():
                    self.deck_pk = path_dict['deck_pk']
                if 'tag' in path_dict.keys():
                    self.tag = path_dict['tag']
                    self.create_room(self.tag)
                else:
                    self.create_room(self.tag)
        else:
            logging.info("find room :: No room name found OR no subject found")
            # quickmatching method
            for room in Room.objects.all():
                if len(room.players.all()) != room.max_players:
                    self.join_room(room)
                    break
            if self.user.player.room is None:
                self.create_room(self.tag)

    def create_room(self, tag):
        logging.info("\t{} creating room".format(self.user))
        player = self.user.player
        room = Room.objects.create()
        room.save()
        player.room = room
        self.hosted_room = room
        # self.user.player.hosted_room = room
        player.save()
        if hasattr(self, "deck_pk") and self.deck_pk is not None:
            if not Deck.objects.filter(pk=self.deck_pk).exists():
                self.choose_random_deck()
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
        if self.scope['url_route']['kwargs']["play_mode"] == "single-player":
            self.game_ready_list_mode()

    def join_room(self, room_object):
        logging.info("\t{} attempting to join Room {}".format(self.user, room_object.pk))
        room = room_object
        user = self.user
        if user.is_authenticated and user.profile not in room.players.all() and len(room.players.all()) < room.max_players:
            logging.info("User {} joined room {}".format(self.scope['user'].id, room.id))
            self.user.player.room = room
            self.user.player.save()
            self.room_group_name = 'room_%s' % room.pk
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )
            self.send_json({"action":"admin", "message": "alloted room %s" % str(room.pk)})
            for playa in room.players.all():
                if playa == self.user.player:
                    pass
                else:
                    async_to_sync(self.channel_layer.group_send)(
                        'user_{}'.format(playa.pk),
                        {
                            "type": "send_json",
                            "action": "opponent",
                            "message": "{} has joined the room".format(self.user),
                        }
                    )

            for playa in room.players.all():
                if playa.pk != self.user.player.pk:
                    self.send_json({"action": "opponent", "message": "Playing against {}".format(playa.user)})

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
                "message": "Room is full... disconnecting from game",
            })
            self.close()

    def leave_room(self):
        logging.info("\tUser {} leaving room {}".format(self.user, self.user.player.room))
        try:
            user = self.scope['user']
            room = self.user.player.room
            if user.is_authenticated and Room.objects.filter(pk=room.pk).exists():
                self.user.player.room.players.remove(self.user.player)
                self.user.player.game_score = 0
                self.user.save()
                logging.info("Room {}".format(room.players.all()))
                for player in room.players.all():
                    logging.info("Still inside is {}".format(player.user))
                room.delete_if_empty()
            # self.close()
        except Exception as e:
            logging.exception(e)

    def receive_json(self, content, **kwargs):
        logging.info("Receiving message from client User {}".format(self.user) )
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
                except Exception as e:
                    logging.exception(e)

            elif type(content) is dict:
                try:
                    get_action = content["action"]
                    get_schema = content["message"]
                    getattr(self, get_action)(get_schema)
                except Exception as e:
                    logging.exception(e)

    def admin(self, message):
        # only to handle admin messages to self
        logging.info("\t{} entering admin handler to do command {}".format(self.user,message))
        getattr(self, message)()

    def game_ready(self):
        logging.info("\t{} entering game handler".format(self.user))
        # TODO start time and counter
        if hasattr(self, "hosted_room"):
            if self.hosted_room == self.user.player.room and len(self.user.player.room.players.all()) == self.user.player.room.max_players:
                self.send_everyone({
                    "action": "admin",
                    "message": "Game is ready",
                })
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

    def game_ready_list_mode(self):
        logging.info("\t{} entering Game Handler (returns list)".format(self.user))
        if hasattr(self, "hosted_room"):
            if self.hosted_room == self.user.player.room and (len(self.user.player.room.players.all()) == self.user.player.room.max_players or self.scope['url_route']['kwargs']['play_mode']=="single-player"):
                self.send_everyone({
                    "action": "admin",
                    "message": "game is ready",
                })
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        "type": "receive_json",
                        "message": {
                            "action": "admin",
                            "schema": "get_article_list",
                        }
                    }
                )

    def respond_specifically_to(self, answers):
        article_pk = answers["article_pk"]
        response = answers["answer"]
        room = self.user.player.room
        logging.info("User {} responding specifically to Article {}".format(self.user.id, article_pk))
        article = Article.objects.get(pk=article_pk)
        result = 0
        if article.truth_value is not None:
            if response == article.truth_value:
                result += 1
        if hasattr(self.user.player, "score"):
            self.user.player.score += result
        else:
            logging.info("Something is wrong with player score values")
            self.user.player.score = result
        self.user.player.game_score += result
        self.send_everyone({
            "action": "result",
            "message": {
                "result": "{} has scored {} points!".format(self.user, result),
            }
        })
        self.user.player.ready = True
        self.user.player.save()
        self.check_ready(room, True)

    def get_article_list(self):
        logging.info("\t{} getting list of articles".format(self.user))
        logging.info(self.user)
        deck = self.user.player.room.deck
        list_articles = deck.articles.values_list(flat=True)
        article_counter = self.user.player.room.article_counter
        if article_counter == len(deck.articles.all()):
            #TODO only host sends signal
            logging.info("GAME ENDED")
            self.user.player.room.article_counter = 0
            self.user.player.room.save()

            if hasattr(self, "hosted_room"):
                if self.hosted_room.pk == self.user.player.room.pk:
                    list_of_scores = self.get_list_of_scores("id")
                    self.send_everyone({
                        "action": "game end",
                        "message": {
                            "score": list_of_scores,
                        }
                    })
                    signals.game_ended.send_robust(sender=self.__class__, room=self.user.player.room, deck=deck, player_scores=self.get_list_of_scores("pk"))
        else:
            articles = deck.articles.all()
            serializer = ArticleSerializer(articles, many=True)
            self.send_json({
                "action": "list of cards",
                "message": str(JSONRenderer().render(serializer.data)),
                # "message": serializers.serialize("json", ArticleSerializer(article))
            })

    def next_article(self):
        logging.info("\t{} getting article".format(self.user))
        logging.info(self.user)
        deck = self.user.player.room.deck
        list_articles = deck.articles.values_list(flat=True)
        article_counter = self.user.player.room.article_counter
        # game end
        if article_counter == len(deck.articles.all()):
            if self.user.player.room.article_counter == len(self.user.player.room.deck.articles.all()):

                logging.info("GAME ENDED")
                self.user.player.room.article_counter = 0
                self.user.player.room.save()

                if hasattr(self, "hosted_room"):
                    if self.hosted_room.pk == self.user.player.room.pk:
                        list_of_scores = self.get_list_of_scores("id")
                        self.send_everyone({
                            "action": "game end result",
                            "message": {
                                "score": list_of_scores,
                            }
                        })
                        signals.game_ended.send_robust(sender=self.__class__, room=self.user.player.room, deck=deck, player_scores=self.get_list_of_scores("pk"))
                        async_to_sync(self.channel_layer.group_send)(
                            self.room_group_name,
                            {
                                "type": "receive_json",
                                "message": {
                                    "action": "admin",
                                    "schema": "close",
                                }
                            }
                        )
        else:
            curr_article = Article.objects.get(pk=list_articles[article_counter])
            #logging.info("getting article")
            self.send_json({
                "action": "card",
                "message": str(JSONRenderer().render(ArticleSerializer(curr_article).data)),
                # "message": serializers.serialize("json", ArticleSerializer(article))
            })

    def check_ready(self, room, is_this_list=False):
        logging.info("\t{} checking if everyone is ready".format(self.user))
        complete_ready = True
        for player in room.players.all():
            if not player.ready:
                complete_ready = player.ready
                break

        if complete_ready:
            if is_this_list:
                self.user.player.room.article_counter += 1
                if self.user.player.room.article_counter == len(self.user.player.room.deck.articles.all()):
                    logging.info("GAME ENDED")
                    self.user.player.room.article_counter = 0
                    self.user.player.room.save()

                    if hasattr(self, "hosted_room"):
                        if self.hosted_room.pk == self.user.player.room.pk:
                            list_of_scores = self.get_list_of_scores("id")
                            self.send_everyone({
                                "action": "game end",
                                "message": {
                                    "score": list_of_scores,
                                }
                            })
                            signals.game_ended.send_robust(sender=self.__class__, room=self.user.player.room, deck=self.user.player.room.deck,
                                                           player_scores=self.get_list_of_scores("pk"))
                            async_to_sync(self.channel_layer.group_send)(
                                self.room_group_name,
                                {
                                    "type": "receive_json",
                                    "message": {
                                        "action": "admin",
                                        "schema": "close",
                                    }
                                }
                            )

                else:
                    self.user.player.ready = False
                    self.user.player.room.save()
            else:
                self.user.player.room.article_counter += 1
                self.user.player.room.save()
                self.next_article()
        else:
            #TODO why never here
            self.send_json({"action": "admin", "message": "Still waiting for all players to answer"})

    def respond(self, message):
        logging.info("\t{} responding".format(self.user))
        logging.info(self.user)
        article_pk = message["article_pk"]
        response = message["answer"]
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
            result = 0
        elif response == -1:
            result = -1
        if hasattr(self.user.player, "score"):
            self.user.player.score += result
        else:
            self.user.player.score = result

        self.user.player.game_score += result

        path_dict = self.scope['url_route']['kwargs']
        if "play_mode" in path_dict.keys():
            if path_dict["play_mode"] == "single-player":
                if response == 1:
                    outcome = True
                elif response == 0:
                    outcome = False
                else:
                    outcome = None
                if outcome == None:
                    pass
                else:
                    signals.article_swiped.send_robust(sender=self.__class__, player=self.user.player, article=Article.objects.get(pk=article_pk), outcome=outcome)

        list_of_scores = self.get_list_of_scores("id")
        self.send_everyone({
            "action": "result",
            "message": {
                "result": {str(self.user): result},
            }
        })
        self.user.player.ready = True
        self.user.player.save()
        self.check_ready(room)

    def get_list_of_scores(self, id_or_pk):
        logging.info("\t{} getting scores".format(self.user))
        room = self.user.player.room
        list_of_scores = {}
        try:
            if id_or_pk == "id":
                for player in room.players.all():
                    list_of_scores[str(player.user)] = player.game_score
            elif id_or_pk == "pk":
                for player in room.players.all():
                    list_of_scores[player.pk] = player.game_score

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
        list_pks = Deck.objects.all().values_list(flat=True)
        self.deck_pk = list_pks[random.randint(0,len(list_pks))]
        if Deck.objects.filter(pk=self.deck_pk).exists() and Deck.objects.get(pk=self.deck_pk).articles.all() is not None:
            logging.info("Playing Deck " + str(self.deck_pk))

        else:
            logging.info("Deck empty")
    def wait_for_disconnect(self):
        if self.user.player.room is not None:
            self.wait_for_disconnect()

    def disconnect(self, code):
        self.leave_room()

