from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        # if self.scope["user"].is_anonymous:
        #     # Reject unauthenticated connections
        #     await self.close()
        # else:

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"group_game_{self.room_name}"
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

    async def receive_json(self, content, **kwargs):
        message = content["message"]
        username = self.scope["user"].username
        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "send_message",
                "message": message,
                "username": username,
            })

    @staticmethod
    async def send_message(event):
        message = event["message"]
        username = event["username"]
        await ChatConsumer.send_json({"message": message, "username": username})
