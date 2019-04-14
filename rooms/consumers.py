from channels.generic.websocket import JsonWebsocketConsumer, WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import Room
from articles.models import Deck, Article
import logging
import json
from django.core import serializers
import random
from articles.serializers import ArticleSerializer,DeckSerializer,TagSerializer
from rest_framework.renderers import JSONRenderer

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
        logging.info("current user is: " + str(self.scope['user']))
        try:
            self.user = self.scope['user']
        except:
            message = "connection error :: either you are not logged in or cannot provide authentication"
            logging.exception(message)
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
        # self.request_to_join(message=message)

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
            # logging.exception(e)

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
        #             logging.info("wow SAME SUBJECT FOUND")
        #             self.join_room(room)
        #         # if there is still no room available
        #         if self.user.player.room is None:
        #             logging.info("all rooms filled")
        #             self.create_room(subject)
        #
        #     # means no room with same subject
        #     else:
        #         logging.info("room doesnt exist")
        #         # create room
        #         self.create_room(subject)

        # quickmatching method
        for room in Room.objects.all():
            if len(room.players.all()) != room.max_players:
                self.join_room(room)
                break
        # logging.info("YOYOYOYOYOYOYO" + str(self.user.player.room))
        # if self.user.player.room is not None:
        #     room = self.user.player.room
        #     room.delete_if_empty()
        #     if self.user.player.room is not None:
        #         #TODO send response
        #         logging.info("player still in room lol")
        #         self.user.player.room.force_delete()
        #         if self.user.player.room is not None:
        #             logging.info("how da fak")
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

        logging.info("User {} CREATED room {}".format(self.scope['user'].id, room.id))
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
        logging.info("room created")
        self.send_everyone({"action": "admin", "message": "created room %s" % str(room.pk)})
        self.send_everyone({"action": "admin", "message": "created room .. waiting for other players to join"})

    def join_room(self, room_object):
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
            logging.info("joined room")
            self.send_everyone({"action":"admin", "message": "alloted room %s" % str(room.pk)})
            # check if game is ready
            if (len(room.players.all()) == room.max_players):
                self.game_ready()

        elif self.user.profile in room.players.all():
            # TODO how to handle if user already in room --> will that happen lol
            logging.info("Already in room bro")

        elif len(room.players.all()) == room.max_players:
            logging.info("room full ==> try again")
            #TODO handle if player wants specific room but full
            # self.send_json({
            #     "action": "admin",
            #     "data": "room is full .. disconnecting from game",
            # })

    def disconnect(self, code):
        logging.info(".. entering disconnect handler ..")
        # logging.info("precheck all rooms")
        # logging.info(Room.objects.all())
        user = self.scope['user']
        room = user.player.room
        # logging.info("deleting room from player and room itself")
        try:
            #TODO what if room is still exists because player disconnects wrongly
            if user.is_authenticated:
                # logging.info("how many people in room :: " + str(len(room.players.all())))
                #TODO fully disociate player from room
                self.user.player.room.players.remove(self.user.player)
                self.user.save()
                logging.info("User {} left room {}".format(user.pk, room.pk))
                room.delete_if_empty()

                logging.info("Please check that room is indeed deleted")
                logging.info(Room.objects.all())
        except Exception as e:
            logging.exception("Disconnect ERROR :::")
            logging.exception(e)

    def receive_json(self, content, **kwargs):
        logging.info(".. receiving message from client ..")

        self.send_json({
            "action": "admin",
            "message": "server received your message"
        })
        # TODO handle bad input types
        # MUST BE double quotes !!! ""
        logging.info("look out for incoming message structure")
        logging.info("incoming message: " + str(content) + "\nmessage type is: " + str(type(content)))

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
        else:
            logging.exception("receive json error :: received class type inconsistent, should be str or dict")

    def admin(self, message):
        logging.info(".. entering admin handler ..")
        getattr(self, message)()

    def game_ready(self):
        # TODO start time and counter
        self.send_json({
            "action": "admin",
            "message": "game is ready",
        })
        self.send_everyone({
            "action": "admin",
            "message": "game is ready",
        })
        self.count=1
        self.next_article()

    def next_article(self):
        logging.info(".. entering article handler ..")
        deck = self.user.player.room.deck
        list = deck.articles.values_list(flat=True)
        # game end
        logging.info(deck)
        logging.info(len(deck.articles.all()))
        if self.count == len(deck.articles.all()):
            logging.info("game finished")
            #TODO finish game
            self.count = 0
        else:
            logging.info("getting article")
            article = Article.objects.get(pk=list[self.count-1])
            logging.info(article)
            # async_to_sync(self.channel_layer.group_send)(
            #     self.room_group_name,
            #     {
            #         "type": "send",
            #         "action": "new card",
            #         "message": JSONRenderer().render(ArticleSerializer(article).data),
            #     })
            self.send_everyone({
                "action": "new card",
                "message": str(JSONRenderer().render(ArticleSerializer(article).data)),
                # "message": serializers.serialize("json", ArticleSerializer(article))
            })
            self.count += 1

    # def article_request(self, article_pk):
    #     try:
    #         if Article.objects.filter(pk=article_pk).exists():
    #             article = serializers.serialize("json", [Article.objects.get(pk=article_pk)])
    #         else:
    #             article = "Article Not Found"
    #         self.send(text_data=json.dumps({
    #             'message': article
    #         }))
    #     except Exception as e:
    #         self.send_json({"message": "improper request sent"})
    #         logging.exception("article request ::: ")
    #         logging.exception(e)

    def update_score(self):
        user = self.scope['user']
        # TODO update score

    def submit_final_score(self):
        user = self.scope['user']

    def send_everyone(self, nested_data):
        logging.info(".. entering sending everyone handler ..")
        # does nested_data still have key "type" ???
        logging.info(nested_data)
        logging.info(type(nested_data))
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
                logging.exception(e)
                self.send_json({
                    "action": "admin",
                    "message": "Your message was not send out, please try again",
                })
        else:
            self.send_json({
                "action": "admin",
                "message": "Can't send message. You're not in any group yet"
            })
