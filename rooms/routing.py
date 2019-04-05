from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('<room_name>/', consumers.RoomConsumer),
    path('game/<room_name>', consumers.GameConsumer)
]
