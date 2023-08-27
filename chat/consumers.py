# chatroom/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from team.models import *
from message.models import *
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
        user_id = text_data_json['user_id']
        user_name = text_data_json['user_name']
        is_at_all = text_data_json['is_at_all']
        array_data = text_data_json.get('array_data', [])
        message_type = text_data_json['message_type']
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user_id': user_id,
                'user_name': user_name,
                'is_at_all': is_at_all,
                'array_data': array_data,
                'message_type': message_type
            }
        )

    async def chat_message(self, event):
        user_id = event['user_id']
        user_name = event['user_name']
        message = event['message']
        is_at_all = event['is_at_all']
        array_data = event['array_data']
        message_type = event['message_type']
        await self.send(text_data=json.dumps({
            'user_id': user_id,
            'user_name': user_name,
            'message': message,
            'is_at_all': is_at_all,
            'array_data': array_data,
            'message_type': message_type
        }))

