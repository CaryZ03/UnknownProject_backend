# # consumers.py
# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
#
#
# class NotificationConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         # 获取当前用户
#         user_id = self.scope['url_route']['kwargs']["user_id"]
#
#         # 接受 WebSocket 连接
#         await self.accept()
#
#         # 将用户添加到组，以便向特定用户发送通知
#         await self.channel_layer.group_add(
#             "user_notification_receiver_" + user_id,
#             self.channel_name
#         )
#
#     async def disconnect(self, close_code):
#         # 获取当前用户
#         user_id = self.scope['url_route']['kwargs']["user_id"]
#
#         # 将用户从组中移除
#         await self.channel_layer.group_discard(
#             "user_notification_receiver_" + user_id,
#             self.channel_name
#         )
#
#     async def receive(self, text_data):
#         # 这里可以处理前端发送的消息
#         pass
#
#     async def send_notification(self, event):
#         # 发送通知给用户的 WebSocket 连接
#         await self.send(text_data=json.dumps(event["message"]))
