import json
import random
from channels.generic.websocket import AsyncWebsocketConsumer


class DocumentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.document_id = self.scope['url_route']['kwargs']['document_id']
        self.document_group_name = f"document_{self.document_id}"
        #self.user_color = f"rgb({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)})"

        # 将用户添加到文档的群组
        await self.channel_layer.group_add(
            self.document_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # 将用户从文档的群组中移除
        await self.channel_layer.group_discard(
            self.document_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        content = data['content']
        #cursor_position = data['cursor_position']

        # 将接收到的内容广播给文档的所有用户
        await self.channel_layer.group_send(
            self.document_group_name,
            {
                'type': 'document_update',
                'content': content,
                #'cursor_position': cursor_position,
                #'user_color': self.user_color
            }
        )

    async def document_update(self, event):
        content = event['content']
        #cursor_position = event['cursor_position']
        #user_color = event['user_color']

        # 将内容发送给WebSocket连接
        await self.send(text_data=json.dumps({
            'content': content,
            #'cursor_position': cursor_position,
            #'user_color': user_color
        }))
