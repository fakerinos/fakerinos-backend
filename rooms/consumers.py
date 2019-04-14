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

"""
### TODOs
1. how to send extra content through json --> subject 
    -- self.scope['url_route']['kwargs'][<url_part_name_self_defined_yeah>]
2. what is in websocket_connect(self,message) ==> WHATS IN MESSAGE
3. ARE WE USING ASYNC TO SYNC
5. WHY DOESNT room 1 WORK ??????
6. SERIOUSLY HOW TO DELETE ROOMS LA
7. How to send dict not text
8. Force connection and find room first
###

types --> determines which handler is called for
vanilla types:
    A. websocket_connect
    B. receive_json
    C. send_json
    D. websocket_disconnect

main receive types:
    A. find_room
        checks if available game (with right subject && has vacancy)
        i. join_room
        else
        ii. create_room

        .. and waits ..
        .. till operational.game_start ..

    B. operational
        i. game_start
        .. creates waiting_list [players.size] ..

        ii. indicate_ready
        .. update all room's waiting lists ..

        iii. next_article && submit score
        #TODO who gets article (?) client || server
        
        iv. submit score
        
    C. message_print
        takes a message and sends to client to print

main send types: 
    A. game_start
    B. next_article
    C. join_room / create_room

"""


class RoomConsumer(JsonWebsocketConsumer):
    def websocket_connect(self, message):
        logging.info(".. entering ws connection handler ..")
        #logging.info("current user is: " + str(self.scope['user']))
        try:
            self.user = self.scope['user']
        except:
            message = "connection error :: either you are not logged in or cannot provide authentication"
            #logging.exception(message)
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
        # TODO deck needs to be initialized YOOOO
        logging.info(".. entering find_room handler ..")
        # url args are given as str
        self.room_pk = None
        self.tag = None
        try:
            self.deck_pk = self.scope['url_route']['kwargs']['tag']
            self.room_pk = self.scope['url_route']['kwargs']['room_pk']

        except Exception as e:
            logging.exception("find room :: No room name found OR no subject found")
            # #logging.exception(e)

        if self.deck_pk is None:
            number_of_decks = len(Deck.objects.all())
            self.deck_pk = random.randint(1, number_of_decks+1)
        #TODO am i searching for subject

        """
        Logic for entering rooms directly and filtering by subject
        """
        # if room_pk != None:
        #     self.join_room(Room.objects.get(pk=room_pk))
        # # TODO get search from input (during connection)
        # # if there is rooms with same subject -> check if avail -> else if not ->
        # else:
        #     if Room.objects.filter(subject=subject).exists():
        #         for room in Room.objects.filter(subject=subject):
        #             #logging.info("wow SAME SUBJECT FOUND")
        #             self.join_room(room)
        #         # if there is still no room available
        #         if self.user.player.room is None:
        #             #logging.info("all rooms filled")
        #             self.create_room(subject)
        #
        #     # means no room with same subject
        #     else:
        #         #logging.info("room doesnt exist")
        #         # create room
        #         self.create_room(subject)

        # quickmatching method
        for room in Room.objects.all():
            if len(room.players.all()) != room.max_players:
                self.join_room(room)
                break
        # if self.user.player.room is not None:
        #     room = self.user.player.room
        #     room.delete_if_empty()
        #     if self.user.player.room is not None:
        #         #TODO send response
        #         #logging.info("player still in room lol")
        #         self.user.player.room.force_delete()
        #         if self.user.player.room is not None:
        #             #logging.info("how da fak")
        #         else:
        #             self.create_room(self.tag)
        #     else:
        #         self.create_room(self.tag)
        if self.user.player.room is None:
            self.create_room(self.tag)


    def create_room(self, tag):
        logging.info(".. entering create room handler ..")
        # TODO create room with subject and add host
        # TODO assign deck
        if tag is not None:
            room = Room.objects.create(tag=tag)
        else:
            room = Room.objects.create(tag=None)
        #logging.info("User {} CREATED room {}".format(self.scope['user'].id, room.id))
        self.user.player.room = room
        self.user.player.hosted_room = room
        self.user.player.save()
        room.deck = Deck.objects.get(pk=self.deck_pk)
        room.save()
        self.room_group_name = 'room_%s' % self.user.player.room.pk
        # TODO create group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        #logging.info("room created")
        signals.player_joined_room.send(sender=self.__class__, room=room, player=self.user.player)
        self.send_everyone({"action": "admin", "message": "created room %s" % str(room.pk)})
        self.send_everyone({"action": "admin", "message": "created room .. waiting for other players to join"})

    def join_room(self, room_object):
        logging.info(".. entering join room ..")
        room = room_object
        if self.user.is_authenticated and self.user.profile not in room.players.all() and len(room.players.all()) < room.max_players:
            #logging.info("User {} joined room {}".format(self.scope['user'].id, room.id))
            self.user.player.room = room
            self.user.player.save()
            self.room_group_name = 'room_%s' % room.pk
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )
            #logging.info("joined room")
            signals.player_joined_room.send(sender=self.__class__, room=room, player=self.user.player)
            self.send_json({"action":"admin", "message": "alloted room %s" % str(room.pk)})
            self.send_everyone({"action": "admin", "message": "User {} has joined the room".format(self.user)})
            # check if game is ready

            if len(room.players.all()) == room.max_players:
                self.game_ready()

        # elif self.user.profile in room.players.all():
        #     # TODO how to handle if user already in room --> will that happen lol
        #     #logging.info("Already in room bro")

        elif len(room.players.all()) == room.max_players:
            #logging.info("room full ==> try again")
            #TODO handle if player wants specific room but full
            self.send_json({
                "action": "admin",
                "message": "room is full .. disconnecting from game",
            })
            self.websocket_disconnect({"code": None})

    def disconnect(self, code):
        logging.info(".. entering disconnect handler ..")
        user = self.scope['user']
        room = user.player.room
        try:
            #TODO what if room is still exists because player disconnects wrongly
            if user.is_authenticated:
                # #logging.info("how many people in room :: " + str(len(room.players.all())))
                #TODO fully disociate player from room
                self.user.player.room.players.remove(self.user.player)
                self.user.save()
                #logging.info("User {} left room {}".format(user.pk, room.pk))
                room.delete_if_empty()
                signals.player_left_room.send(sender=self.__class__, room=room, player=self.user.player)
                #logging.info("Please check that room is indeed deleted")
                #logging.info(Room.objects.all())

                try:
                    for group in self.groups:
                        async_to_sync(self.channel_layer.group_discard)(
                            group, self.channel_name
                        )
                except AttributeError:
                    raise InvalidChannelLayerError(
                        "BACKEND is unconfigured or doesn't support groups"
                    )
                raise StopConsumer()

        except Exception as e:
            logging.exception("Disconnect ERROR :::")
            #logging.exception(e)

    def receive_json(self, content, **kwargs):
        logging.info(".. receiving message from client ..")

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
                #logging.info("uh huh")
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
        logging.info(".. entering admin handler ..")
        getattr(self, message)()

    def game_ready(self):
        logging.info(".. entering game handler ..")
        # TODO start time and counter
        self.send_everyone({
            "action": "admin",
            "message": "game is ready",
        })
        self.send_everyone({"action": "create_game_results", "message": None})
        self.next_article()

    # def create_game_results(self):
        signals.game_started.send(sender=self.__class__, room=self.user.player.room, deck=self.user.player.room.deck)

    def next_article(self):
        logging.info(".. entering article handler ..")
        deck = self.user.player.room.deck
        list_articles = deck.articles.values_list(flat=True)
        article_counter = self.user.player.room.article_counter
        # game end
        if article_counter == len(deck.articles.all()):
            #TODO only host sends signal
            logging.info("GAME ENDED")
            self.user.player.room.article_counter = 0
            self.user.player.room.save()

            list_of_scores = self.get_list_of_scores()
            self.send_everyone({
                "action": "game end",
                "message": {
                    "score": list_of_scores,
                }
            })
            #TODO clean up disconnection
            signals.game_started.send(sender=self.__class__, room=self.user.player.room, deck=deck, game_uid=self.user.player.room.pk, scores=list_of_scores)
            self.websocket_disconnect({"code": None})
        else:
            curr_article = Article.objects.get(pk=list_articles[article_counter])
            #logging.info("getting article")
            self.send_everyone({
                "action": "new card",
                "message": str(JSONRenderer().render(ArticleSerializer(curr_article).data)),
                # "message": serializers.serialize("json", ArticleSerializer(article))
            })

    def check_ready(self, room):
        logging.info(".. checking if everyone is ready ..")
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
        logging.info(".. entering response handler ..")
        response = message["response"]
        time_remaining = message["time_remaining"]
        # 0 for false 1 for true
        result = 0
        room = self.user.player.room
        deck = self.user.player.room.deck
        list_articles = deck.articles.values_list(flat=True)
        article_counter = self.user.player.room.article_counter
        curr_article = Article.objects.get(pk=list_articles[article_counter])

        if response == curr_article.truth_value:
            result = 1
        elif response != curr_article.truth_value:
            result = -1
        if hasattr(self.user.player, "score"):
            self.user.player.score += result
        else:
            #logging.info("Something is wrong with player score values")
            self.user.player.score = result

        list_of_scores = self.get_list_of_scores()
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

    def get_list_of_scores(self):
        logging.info(".. getting scores ..")
        room = self.user.player.room
        list_of_scores = {}

        try:
            for player in room.players.all():
                list_of_scores[str(player.user)] = player.score

        except Exception as e:
            logging.exception("Error in getting list of player scores")
            #logging.exception(e)
        return list_of_scores


    def submit_final_score(self):
        user = self.scope['user']

    def send_everyone(self, nested_data):
        logging.info(".. entering sending everyone handler ..")
        # does nested_data still have key "type" ???
        #logging.info(nested_data)
        #logging.info(type(nested_data))
        if hasattr(self, "room_group_name"):
            try:
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
