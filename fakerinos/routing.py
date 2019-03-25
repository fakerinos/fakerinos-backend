from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from fakerinos.middleware import TokenAuthMiddlewareStack
from django.urls import path
import chat.routing
import rooms.routing

application = ProtocolTypeRouter(
    {
        'websocket': TokenAuthMiddlewareStack(
            URLRouter([
                path('ws', URLRouter([
                    path('chat', URLRouter(chat.routing.websocket_urlpatterns)),
                    path('rooms', URLRouter(rooms.routing.websocket_urlpatterns)),
                ]))]
            )
        ),
    }
)
