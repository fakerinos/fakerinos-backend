from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('<subject>/', consumers.RoomConsumer),
    # path('<subject>/<room_pk>/', consumers.RoomConsumer),
    ]
