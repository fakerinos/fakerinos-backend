from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
from fakerinos.middleware import TokenAuthMiddlewareStack
from django.urls import path
import rooms.routing

application = ProtocolTypeRouter(
    {
        'websocket': TokenAuthMiddlewareStack(
            URLRouter([
                path('ws', URLRouter([
                    path('rooms/', URLRouter(rooms.routing.websocket_urlpatterns)),
                ]))]
            )
        ),
    }
)
