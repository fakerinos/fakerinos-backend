from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('<room_name>/<deck_name>/', consumers.RoomConsumer)
]
