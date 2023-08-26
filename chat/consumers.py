# chatroom/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from user.models import User

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        # user_id = text_data_json['user_id']
        # user_name = text_data_json['user_name']

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                # 'user_id': user_id,
                # 'user_name': user_name
            }
        )

    async def chat_message(self, event):
        # user_id = event['user_id']
        # user_name = event['user_name']
        message = event['message']
        await self.send(text_data=json.dumps({
            # 'user_id': user_id,
            # 'user_name': user_name,
            'message': message,
        }))

