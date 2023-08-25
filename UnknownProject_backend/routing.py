# chatroom_project/routing.py
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

from chat import routing as chatroom_routing

application = ProtocolTypeRouter({
    "websocket": URLRouter(
        chatroom_routing.websocket_urlpatterns
    ),
})
