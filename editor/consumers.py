import json
import random
from channels.generic.websocket import AsyncWebsocketConsumer


class DocumentConsumer(AsyncWebsocketConsumer):
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
        message = text_data_json['message']
        x_off = text_data_json['x_off']
        y_off = text_data_json['y_off']
        x_scale = text_data_json['x_scale']
        y_scale = text_data_json['y_scale']
        x_canvas = text_data_json['x_canvas']
        y_canvas = text_data_json['y_canvas']
        print(message)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'edit_message',
                'message': message,
                'x_off': x_off,
                'y_off': y_off,
                'x_scale': x_scale,
                'y_scale': y_scale,
                'x_canvas': x_canvas,
                'y_canvas': y_canvas
            }
        )

    async def edit_message(self, event):
        message = event['message']
        x_off = event['x_off']
        y_off = event['y_off']
        x_scale = event['x_scale']
        y_scale = event['y_scale']
        x_canvas = event['x_canvas']
        y_canvas = event['y_canvas']
        print(message)
        await self.send(text_data=json.dumps({
            'message': message,
            'x_off': x_off,
            'y_off': y_off,
            'x_scale': x_scale,
            'y_scale': y_scale,
            'x_canvas': x_canvas,
            'y_canvas': y_canvas
        }))
