import asyncio
import websockets
import json
from rest_framework.test import APITestCase


class TestingWebsockets(APITestCase):

    async def client_1(self, uri):
        print(uri)
        async with websockets.connect(uri, extra_headers={'Authorization': "Token 9abda1f94550ad23d4bcb78b91c552dae049bf6e"}) as websocket:
            await websocket.send(json.dumps({"action": "admin", "message": "request_to_join"}))

            while True:
                output = await websocket.recv()
                joutput = json.loads(output)
                print(joutput)
                #simulate player response
                if joutput["action"] == "card":
                    await websocket.send(json.dumps({"action": "respond", "message": {"article_pk": 1, "answer": 1}}))
                # simulate game timout
                if joutput["action"] == "result" and "type" in joutput.keys():
                    print("TIMEOUT")
                    await websocket.send(json.dumps({"action": "respond", "message": {"article_pk": 1, "answer": -1}}))
                # simulate game ready
                if joutput["action"] == "opponent":
                    await websocket.send(json.dumps({"action": "admin", "message": "game_ready"}))

    def game_test_1(self):
        asyncio.get_event_loop().run_until_complete(
                    self.client_1('wss://fakerinos.herokuapp.com/ws/rooms/'))

    async def client_2(self, uri):
        print(uri)
        async with websockets.connect(uri, extra_headers={'Authorization': "Token 5c6a6ccbac338d1d474fb42b2064f9b8e0ecc268"}) as websocket:
            await websocket.send(json.dumps({"action": "admin", "message": "request_to_join"}))

            while True:
                output = await websocket.recv()
                joutput = json.loads(output)
                print(joutput)
                #simulate player response
                if joutput["action"] == "card":
                    await websocket.send(json.dumps({"action": "respond", "message": {"article_pk": 1, "answer": 1}}))
                # simulate game timout
                if joutput["action"] == "result" and "type" in joutput.keys():
                    print("TIMEOUT")
                    await websocket.send(json.dumps({"action": "respond", "message": {"article_pk": 1, "answer": -1}}))
                # simulate game ready
                if joutput["action"] == "opponent":
                    await websocket.send(json.dumps({"action": "admin", "message": "game_ready"}))
        def game_test_2(self):
            asyncio.get_event_loop().run_until_complete(
                        self.game_test_2('wss://fakerinos.herokuapp.com/ws/rooms/'))
