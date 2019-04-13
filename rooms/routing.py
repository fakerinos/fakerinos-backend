from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('', consumers.RoomConsumer),
    path('<tag>/', consumers.RoomConsumer),
    # path('<tag>/<room_pk>/', consumers.RoomConsumer),
    ]

