import json
import random
from channels.generic.websocket import AsyncWebsocketConsumer


class RedConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"editor_{self.room_name}"

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
        room_id = text_data_json.get('room_id')
        print(room_id)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'edit_message',
                'room_id': room_id
            }
        )

    async def edit_message(self, event):
        room_id = event['room_id']
        print(room_id)
        await self.send(text_data=json.dumps({
            'room_id': room_id
        }))
