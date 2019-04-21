from channels.generic.websocket import JsonWebsocketConsumer, WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import Room, GameResult
from articles.models import Deck, Article
import logging
import json
import random
from articles.serializers import ArticleSerializer,DeckSerializer,TagSerializer

from . import signals


class RoomConsumer(JsonWebsocketConsumer):
    def websocket_connect(self, message):
        try:
            self.user = self.scope['user']
        except:
            message = "Connection error :: either you are not logged in or cannot provide authentication"
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
            "message": "Connection success"
        })

    def request_to_join(self):
        logging.info("\t{} requesting to join a room".format(self.user))
        self.room_pk = None
        self.tag = None
        self.play_mode = "multi-player"

        path_dict = self.scope['url_route']['kwargs']
        if "play_mode" in path_dict.keys():
            if path_dict["play_mode"] == "single-player" or path_dict["play_mode"] == "crowd-source":
                self.play_mode = path_dict["play_mode"]
                if 'deck_pk' in path_dict.keys():
                    self.deck_pk = path_dict['deck_pk']
                if 'tag' in path_dict.keys():
                    self.tag = path_dict['tag']
                    self.create_room(self.tag)
                else:
                    self.create_room(self.tag)
            else:
                self.close()
        else:
            logging.info("find room :: No room name found OR no subject found")
            # quickmatching method
            for room in Room.objects.all():
                logging.info("{} still checking".format(self.user))
                if len(room.players.all()) != room.max_players:
                    self.join_room(room)
                    break
            logging.info(self.user.player.room)
            if self.user.player.room is None:
                logging.info("here")
                self.create_room(self.tag)

    def create_room(self, tag):
        logging.info("\t{} creating room".format(self.user))
        player = self.user.player
        room = Room.objects.create()
        room.save()
        player.room = room
        self.hosted_room = room
        # self.user.player.hosted_room = room
        player.ready = False
        player.game_score = 0
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
        # self.send_everyone({"action": "admin", "message": "created room %s" % str(room.pk)})
        # self.send_everyone({"action": "admin", "message": "created room .. waiting for other players to join"})
        if "play_mode" in self.scope['url_route']['kwargs'].keys():
            if self.scope['url_route']['kwargs']["play_mode"] == "single-player":
                self.game_ready_list_mode()

    def join_room(self, room_object):
        logging.info("\t{} attempting to join Room {}".format(self.user, room_object.pk))
        room = room_object
        user = self.user
        if user.is_authenticated and user.profile not in room.players.all() and len(room.players.all()) < room.max_players:
            logging.info("User {} joined room {}".format(self.scope['user'].id, room.id))
            self.user.player.room = room
            self.user.player.ready = False
            self.user.player.game_score = 0
            self.user.player.save()
            room.players_waiting = 0
            room.article_counter = 0
            room.save()
            self.room_group_name = 'room_%s' % room.pk
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )
            for playa in room.players.all():
                if playa == self.user.player:
                    pass
                else:
                    async_to_sync(self.channel_layer.group_send)(
                        'user_{}'.format(playa.pk),
                        {
                            "type": "send_json",
                            "action": "opponent",
                            "message": "{}".format(self.user),
                        }
                    )

            for playa in room.players.all():
                if playa.pk != self.user.player.pk:
                    self.send_json({"action": "opponent", "message": "{}".format(playa.user)})

        elif self.user.profile in room.players.all():
            logging.info("Already in room bro")

        elif len(room.players.all()) == room.max_players:
            #logging.info("room full ==> try again")
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
                self.user.player.ready = False
                self.user.save()
                logging.info("Room {}".format(room.players.all()))
                for player in room.players.all():
                    logging.info("Still inside is {}".format(player.user))
                room.delete_if_empty()
            # self.close()
        except Exception as e:
            logging.exception(e)

    def receive_json(self, content, **kwargs):
        # logging.info("Receiving message from client User {}".format(self.user) )
        if "type" in content.keys():
            get_action = content["message"]["action"]
            get_schema = content["message"]["schema"]
            getattr(self, get_action)(get_schema)
        else:
            self.send_json({
                "action": "admin",
                "message": "Server received your message"
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
        # logging.info("\t{} entering admin handler to do command {}".format(self.user,message))
        getattr(self, message)()

    def game_ready(self):
        logging.info("\t{} entering game handler".format(self.user))
        room = self.user.player.room
        max_player = 1
        if self.play_mode == "multi-player":
            max_player = 2
        self.user.player.ready = True
        self.user.player.save()
        letsgo = True
        if len(room.players.all()) == max_player:
            for player in room.players.all():

                if player.ready is not True:
                    letsgo = False
                    break
        if letsgo:
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    "type": "send_json",
                    "action": "admin",
                    "message": "Game is ready",

                }
            )
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
        else:
            self.send_json({
                "action": "admin",
                "message": "Not everyone ready"
            })

    def next_article(self):
        logging.info("\t{} getting article".format(self.user))
        player = self.user.player
        self.user.player.ready = False
        self.user.player.save()
        room = self.user.player.room
        # room.players_waiting = 1
        room.save()
        deck = self.user.player.room.deck
        list_articles = deck.articles.values_list(flat=True)
        article_counter = room.article_counter
        # game end
        logging.info("{} is seeing {} vs fixed {}".format(self.user, article_counter, len(deck.articles.all())))
        if article_counter == len(deck.articles.all()):
            if hasattr(self, "hosted_room"):
                if self.hosted_room.pk == room.pk:
                    logging.info("GAME ENDED")
                    room.article_counter = 0
                    room.save()
                    list_of_scores = self.get_list_of_scores("id")
                    self.send_everyone({
                        "action": "game end result",
                        "message": {
                            "score": list_of_scores,
                        }
                    })
                    signals.game_ended.send_robust(sender=self.__class__, room=room, deck=deck, player_scores=self.get_list_of_scores("pk"))
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
            # self.send_json({
            #     "action": "card",
            #     "message": str(ArticleSerializer(curr_article).data)
            #     # "message": serializers.serialize("json", ArticleSerializer(article))
            # })
            serializer = ArticleSerializer(curr_article)
            serialized_data = serializer.data
            serialized_data["action"] = "card"
            # logging.info(serialized_data)
            self.send_json(serialized_data)

    def check_ready(self, room, is_this_list=False):
        logging.info("\t{} checking if everyone is ready".format(self.user))
        complete_ready = True

        player = self.user.player
        room = self.user.player.room

        for players in room.players.all():
            if not players.ready:
                complete_ready = players.ready
                break
        logging.info("JUST TO SEE {} sees {} players waiting".format(self.user, self.user.player.room.players_waiting))

        if complete_ready:
            self.user.player.room.article_counter += 1
            self.user.player.room.save()
            self.user.player.room.players_waiting = 0
            self.user.player.room.save()
            logging.info("CHECK THIS OUT {}".format(room.players_waiting))
            if hasattr(self, "hosted_room"):
                if self.hosted_room == room:
                    logging.info("after saving {} waiting".format(self.user.player.room.players_waiting))
                    if is_this_list:
                        if room.article_counter == len(room.deck.articles.all()):
                            self.next_article()
                        else:
                            player.ready = False
                            player.save()
                    else:
                        # check only once
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
        else:
            self.send_json({"action": "admin", "message": "Still waiting for all players to answer"})

    def respond(self, message):
        logging.info("\t{} responding".format(self.user))
        logging.info(message)
        article_pk = message["article_pk"]
        response = message["answer"]
        # 0 for false 1 for true
        result = 0
        player = self.user.player
        room = player.room
        deck = room.deck
        list_articles = deck.articles.values_list(flat=True)
        article_counter = room.article_counter
        curr_article = Article.objects.get(pk=list_articles[article_counter])

        if response == -1:
            self.user.player.ready = True
            self.user.player.room.players_waiting += 1
            self.user.player.save()
            self.user.player.room.save()
            self.check_ready(room)

        elif not player.ready:
            if response != -1:
                if response == curr_article.truth_value:
                    result = 1
                player.game_score += result

                for playa in room.players.all():
                    if playa == self.user.player:
                        pass
                    else:
                        async_to_sync(self.channel_layer.group_send)(
                            'user_{}'.format(playa.pk),
                            {
                                "type": "send_json",
                                "action": "result",
                                "message": {
                                    "opponent": result,
                                    "explanation": curr_article.explanation,
                                }
                            }
                        )

                for playa in room.players.all():
                    if playa.pk != self.user.player.pk:
                        self.send_json({"action": "result", "self": result, "explanation": curr_article.explanation})

                path_dict = self.scope['url_route']['kwargs']
                if "play_mode" in path_dict.keys():
                    if path_dict["play_mode"] == "crowd-source":
                        if response == 1:
                            outcome = True
                        elif response == 0:
                            outcome = False
                        else:
                            outcome = None
                        if outcome is None:
                            pass
                        else:
                            signals.article_swiped.send_robust(sender=self.__class__, player=player, article=Article.objects.get(pk=article_pk), outcome=outcome)
            player.ready = True
            player.save()
            # self.check_ready(room)


    def get_list_of_scores(self, id_or_pk):
        # logging.info("\t{} getting scores".format(self.user))
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
        list_pks = Deck.objects.all().values_list(flat=True)
        pre_assignment_check = list_pks[random.randint(0,len(list_pks)-1)]
        if Deck.objects.filter(pk=pre_assignment_check).exists() and Deck.objects.get(pk=pre_assignment_check).articles.all() is not None:
            self.deck_pk=pre_assignment_check
            # logging.info("Playing Deck " + str(self.deck_pk))

        else:
            logging.info("Deck empty")
            logging.info("attempting to get but failed deck pk {}".format(self.deck_pk))

    def disconnect(self, code):
        self.leave_room()

