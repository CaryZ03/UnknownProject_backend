# chatroom_project/routing.py
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

from chat import routing as chatroom_routing
from consumers.AvatarConsumer import UserAvatarConsumer
from editor.consumers import DocumentConsumer

application = ProtocolTypeRouter({
    "websocket": URLRouter(
        [
            path("ws/document/<str:document_id>/", DocumentConsumer),
            path("ws/upload/avatar/user/", UserAvatarConsumer),
            # path("ws/document/<str:document_id>/", DocumentConsumer),
        ] + chatroom_routing.websocket_urlpatterns,

    ),
})
