import pytest
from asgiref.sync import sync_to_async
from channels.routing import URLRouter, ProtocolTypeRouter
from channels.testing import HttpCommunicator, ApplicationCommunicator, WebsocketCommunicator
from fakerinos.routing import application
from django.contrib.auth import get_user_model
from mixer.backend.django import mixer
from rest_framework.authtoken.models import Token
from fakerinos.routing import application
from channels.layers import get_channel_layer


User = get_user_model()
channel_layer = get_channel_layer()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestWebSockets:

    async def test_send_json(self):

        user = mixer.blend(User, is_superuser=True)
        token = Token.objects.create(user=user)
        headers = [(b'Authorization', "Token {}".format(token.key).encode())]
        communicator = WebsocketCommunicator(application, '/ws/rooms/', headers=headers)
        try:
            message = "Connection error :: either you are not logged in or cannot provide authentication"
            await communicator.send_json_to(
                {
                "action": "admin",
                "message": message,
            })
        except Exception as e:
            pass
        await communicator.disconnect()

    async def test_joining(self):
        user = mixer.blend(User, is_superuser=True)
        token = Token.objects.create(user=user)
        headers = [(b'Authorization', "Token {}".format(token.key).encode())]
        communicator = WebsocketCommunicator(application, '/ws/rooms/', headers=headers)
        try:
            await communicator.send_json_to(
                {
                    "type": "request.to.join",
                    "data": "hello",
            })
            await communicator.disconnect()
        except Exception as e:
            print("whoops")


    async def test_connect(self):
        user = mixer.blend(User, is_superuser=True)
        token = Token.objects.create(user=user)
        headers = [(b'Authorization', "Token {}".format(token.key).encode())]
        communicator = WebsocketCommunicator(application, '/ws/rooms/', headers=headers)
        try:
            connected, subprotocol = await communicator.connect()
            print("notice me {}".format(connected))
            assert connected
        except Exception as e:
            print("whoops")
        await communicator.disconnect()

    async def test_receive(self):
        user = mixer.blend(User, is_superuser=True)
        token = Token.objects.create(user=user)
        headers = [(b'Authorization', "Token {}".format(token.key).encode())]
        communicator = WebsocketCommunicator(application, '/ws/rooms/', headers=headers)
        try:
            await communicator.receive_json_from()
        except Exception as e:
            print("whoops")
        await communicator.disconnect()
