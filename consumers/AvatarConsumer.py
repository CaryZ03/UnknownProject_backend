import base64
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.files.base import ContentFile
from asgiref.sync import sync_to_async

from user.models import User


class UserAvatarConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data_json = json.loads(text_data)
        user_id = 1
        data = data_json.get('data')
        print(user_id)

        user = await self.get_user_by_id(user_id)

        if user:
            # Decode and save the file
            image = ContentFile(base64.b64decode(data), name=f"{user.user_id}.png")
            user.user_avatar.save(image.name, image)
            await self.save_user(user)
            await self.send(text_data=json.dumps({'message': 'File uploaded successfully.'}))

    @sync_to_async
    def get_user_by_id(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @sync_to_async
    def save_user(self, user):
        user.save()

    # async def receive(self, text_data):
    #     data_json = json.loads(text_data)
    #     data = data_json.get('data')
    #
    #     # Decode and save the file
    #     decoded_data = base64.b64decode(data)
    #     file_name = f"uploaded_file_{self.channel_name}.png"  # Generate a unique file name
    #     with open(file_name, 'wb') as f:
    #         f.write(decoded_data)
    #
    #     await self.send(text_data=json.dumps({'message': 'File uploaded successfully.'}))
