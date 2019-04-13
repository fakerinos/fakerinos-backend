from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('', consumers.RoomConsumer),
    path('<deck_pk>/', consumers.RoomConsumer),
    # path('<deck_pk>/<room_pk>/', consumers.RoomConsumer),
    ]
