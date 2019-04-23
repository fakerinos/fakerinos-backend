import pytest
from asgiref.sync import sync_to_async
from channels.routing import URLRouter, ProtocolTypeRouter
from channels.testing import HttpCommunicator, ApplicationCommunicator, WebsocketCommunicator
from fakerinos.routing import application
from django.contrib.auth import get_user_model
from mixer.backend.django import mixer
from django.http import request
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from rest_framework import status
from ..consumers import RoomConsumer

User = get_user_model()


# @pytest.mark.django_db(transaction=True)
# class testConsumers(APITestCase):
#     def setUp(self):
#         # create token
#         self.user = mixer.blend(User)
#         self.token = Token.objects.create(user=self.user)
#         self.headers = [(b'authorization', "Token {}".format(self.token.key).encode())]
#         self.communicator = WebsocketCommunicator(application, "ws/rooms/", headers=self.headers)
#
#     @pytest.mark.asyncio
#     def login(self):
#         connected, subprotocol = await self.communicator.connect()
#         return connected, subprotocol
#
#     @pytest.mark.asyncio
#     def test_login(self):
#         connected, _ = await self.login()
#         assert connected
#
#     @pytest.mark.asyncio
#     def test_send_text_data(self):
#         connected, _ = await self.login()
#         await self.communicator.send_to(text_data="hello")
#         response = await self.communicator.receive_from()
#         assert "hello" == await self.communicator.receive_from()
#         # # Close
#         # await self.communicator.disconnect()
#
#     @pytest.mark.asyncio
#     def test_data_base(self):
#         print("hello")
#         _, _ = self.login()
#         await self.communicator.send_json_to({'type': 'article_request', 'input': 0})
#         response = await self.communicator.receive_from()
#         print(response)
#         self.assertEqual(response.status, status.HTTP_200_OK)
#         assert response.status == status.HTTP_200_OK
#         assert 0 == response['headline']

async def test_connect():
    user = mixer.blend(User)
    token = Token.objects.create(user=user)
    headers = [(b'authorization', "Token {}".format(token.key).encode())]
    communicator = WebsocketCommunicator(RoomConsumer, '/ws/rooms/', headers)
    connected, subprotocol = await communicator.connect()
    print("notice me {}".format(connected))
    assert connected
    await communicator.disconnect()
