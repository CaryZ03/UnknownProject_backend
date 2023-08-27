import base64
import json
import os
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.files.base import ContentFile
from asgiref.sync import sync_to_async
from django.conf import settings

from user.models import User


class UserAvatarConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data_json = json.loads(text_data)
        user_id = data_json.get('user_id')
        data = data_json.get('data')

        # Decode and save the file
        decoded_data = base64.b64decode(data)

        # Specify the directory path within MEDIA_ROOT where you want to save the file
        save_directory = os.path.join(settings.MEDIA_ROOT, 'avatar', 'user')

        # Ensure the directory exists
        os.makedirs(save_directory, exist_ok=True)

        file_name = f"{user_id}.png"  # Generate a unique file name
        file_path = os.path.join(save_directory, file_name)

        with open(file_path, 'wb') as f:
            f.write(decoded_data)

        await self.send(text_data=json.dumps({'message': 'File uploaded successfully.'}))

    async def send(self, text_data):
        pass


class TeamAvatarConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data_json = json.loads(text_data)
        team_id = data_json.get('team_id')
        data = data_json.get('data')

        # Decode and save the file
        decoded_data = base64.b64decode(data)

        # Specify the directory path within MEDIA_ROOT where you want to save the file
        save_directory = os.path.join(settings.MEDIA_ROOT, 'avatar', 'team')

        # Ensure the directory exists
        os.makedirs(save_directory, exist_ok=True)

        file_name = f"{team_id}.png"  # Generate a unique file name
        file_path = os.path.join(save_directory, file_name)

        with open(file_path, 'wb') as f:
            f.write(decoded_data)

        await self.send(text_data=json.dumps({'message': 'File uploaded successfully.'}))

    async def send(self, text_data):
        pass


class ProjectAvatarConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data_json = json.loads(text_data)
        project_id = data_json.get('project_id')
        data = data_json.get('data')

        # Decode and save the file
        decoded_data = base64.b64decode(data)

        # Specify the directory path within MEDIA_ROOT where you want to save the file
        save_directory = os.path.join(settings.MEDIA_ROOT, 'avatar', 'project')

        # Ensure the directory exists
        os.makedirs(save_directory, exist_ok=True)

        file_name = f"{project_id}.png"  # Generate a unique file name
        file_path = os.path.join(save_directory, file_name)

        with open(file_path, 'wb') as f:
            f.write(decoded_data)

        await self.send(text_data=json.dumps({'message': 'File uploaded successfully.'}))

    async def send(self, text_data):
        pass
