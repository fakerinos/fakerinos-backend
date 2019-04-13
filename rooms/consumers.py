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
import sys

"""
### TODOs
1. how to send extra content through json --> subject 
    -- self.scope['url_route']['kwargs'][<url_part_name_self_defined_yeah>]
2. what is in websocket_connect(self,message) ==> WHATS IN MESSAGE
3. ARE WE USING ASYNC TO SYNC
4. ROOM must have host
5. WHY DOESNT room 1 WORK ??????
6. SERIOUSLY HOW TO DELETE ROOMS LA
7. How to send dict not text
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
                "data": message,
            })
            self.close()
        self.accept()
        self.send_json({
            "action": "admin",
            "data": "connection success"
        })
        self.find_room(message=message)

    def find_room(self, message):
        #TODO deck needs to be initialized YOOOO
        logging.info(".. entering find_room handler ..")
        # url args are given as str
        room_pk = None
        subject = None
        try:
            room_pk = self.scope['url_route']['kwargs']['room_pk']
            subject = self.scope['url_route']['kwargs']['subject']
        except Exception as e:
            logging.exception("find room :: No room name found OR no subject found")
            logging.exception(e)

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

        #TODO quickmatching
        for room in Room.objects.all():
            if room.players.all() != room.max_players:
                self.join_room(room)
                break
        if self.user.player.room is None:
            self.create_room(subject)


    def create_room(self, subject):
        logging.info(".. entering create room handler ..")
        # TODO create room with subject and add host
        if subject!=None:
            room = Room.objects.create(subject=subject)
        else:
            room = Room.objects.create(subject=None)
        logging.info("User {} CREATED room {}".format(self.scope['user'].id, room.id))
        self.user.player.room = room
        self.user.player.save()
        self.room_group_name = 'room_%s' % self.user.player.room.pk
        # TODO create group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        logging.info("room created")
        self.send_everyone({"action": "admin", "data": "created room .. waiting for other players to join"})

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
            self.send_everyone({"action":"admin", "data": "joined room"})

        elif self.user.profile in room.players.all():
            # TODO how to handle if user already in room --> will that happen lol
            logging.info("Already in room bro")
            return None

        elif len(room.players.all()) == room.max_players:
            logging.info("room full ==> try again")
            #TODO handle if player wants specific room but full
            # self.send_json({
            #     "action": "admin",
            #     "data": "room is full .. disconnecting from game",
            # })

    def disconnect(self, code):
        logging.info(".. entering disconnect handler ..")
        logging.info("precheck all rooms")
        logging.info(Room.objects.all())
        user = self.scope['user']
        room = user.player.room
        logging.info("deleting room from player and room itself")
        try:
            #TODO what if room is still exists because player disconnects wrongly
            if user.is_authenticated:
                # logging.info("how many people in room :: " + str(len(room.players.all())))
                user.player.room = None
                user.save()
                # logging.info("just for good measure")
                # logging.info(user.player.room)
                # logging.info(user.player.hosted_room)
                # if user.player.hosted_room.pk == room.pk:
                #     logging.info('yes same')
                # logging.info("so you left ?")
                logging.info("REALLY ??? :: " + str(len(room.players.all())))
                logging.info("User {} left room {}".format(user.pk, room.pk))
                room.delete_if_empty()
                logging.info("confirm room is deleted")
                logging.info(Room.objects.all())
        except Exception as e:
            logging.exception("Disconnect ERROR :::")
            logging.exception(e)

    def receive_json(self, content, **kwargs):
        logging.info("######################### receiving data from client ##########################")
        self.send_json({
            "action": "admin",
            "data": "server received your message"
        })
        # TODO handle bad input types
        # MUST BE double quotes !!! ""
        logging.debug("look out for incoming data structure")
        logging.debug("incoming data: " + str(content) + "\ndata type is: " + str(type(content)))

        # handle both string and dict type
        if type(content) is str:
            try:
                content_message = json.loads(content)
                get_type = content_message["type"]
                get_message_to_handler = content_message["message"]
                getattr(self, get_type)(get_message_to_handler)
                logging.info("uh huh")
            except Exception as e:
                logging.exception(e)

        elif type(content) is dict:
            try:
                get_action = content["action"]
                get_data = content["data"]
                getattr(self, get_action)(get_data)
            except Exception as e:
                logging.exception(e)
        else:
            logging.exception("receive json error :: received class type inconsistent, should be str or dict")


    def start_game(self, message):
        #TODO check if user is host and check his game
        #TODO send everyone article
        #TODO get specific articles
        # Anyone can start game model
        async_to_sync(self.channel_layer.group_send)({
            self.room_group_name,
            {
                "type": "article_request",
                "message": json.dumps('{"message": 1}'),
            }
        })
        # doesnt work
        self.send_everyone(self.article_request(1))

        #TODO start time and counter

    def article_request(self, article_pk):
        try:
            if Article.objects.filter(pk=article_pk).exists():
                article = serializers.serialize("json", [Article.objects.get(pk=article_pk)])
            else:
                article = "Article Not Found"
            self.send(text_data=json.dumps({
                'message': article
            }))
        except Exception as e:
            self.send_json({"message": "beeeeeeeech you cant even send request properly like whaaAaaAAAaaAAttT"})
            logging.exception("article request ::: ")
            logging.exception(e)

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
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "send_json",
                "action": nested_data["action"],
                "data": nested_data["data"],
            }
        )



# class GameConsumer(WebsocketConsumer):
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         async_to_sync(self.channel_layer.group_add)(
#             "gameconsumer",
#             self.channel_name
#         )
#
#     def websocket_connect(self, message):
#         """self.game_group_name = 'game_%s'"""
#         self.accept()
#
#     def websocket_disconnect(self, message):
#         """
#         # async_to_sync(self.channel_layer.send(
#         #
#         # ))"""

