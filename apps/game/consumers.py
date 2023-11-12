from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
import json
from .models import Player, Room
from channels.db import database_sync_to_async
from django.db import connection
from asgiref.sync import sync_to_async
from django.db.models import Q


class ChatConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_group_name = None
        self.room_code = None
        self.room_id = None
        self.player_code = None
        self.player_id = None

    async def connect(self):
        self.room_code = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"group_game_{self.room_code}"
        self.room_id = await database_sync_to_async(Room.objects.get)(room_code=self.room_code)
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        print("disconnect player ->", self.player_code)
        # await Player.objects.filter(player_code=self.player_code).adelete()
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "send_message",
                "player_code": self.player_code,
                "action": 'close'
            }
        )

    async def receive_json(self, content, **kwargs):
        chanel_type = ""
        try:
            if content["action"] == "join":
                if self.player_code is not None:
                    content["player_code"] = self.player_code
                nickname = content["nickname"]
                player_code = content["player_code"]
                await database_sync_to_async(self.create_player)(self.room_code, nickname, player_code)
                content["type"] = "send_message"
            if content["action"] == "question":
                content["type"] = "send_question"
            if content["action"] == "answer":
                content["type"] = "send_waitroom_update"
            if content["action"] == "shuffle_players":
                content["type"] = "send_shuffle_players_update"
        except Exception as e:
            print("error", e)

        print('receive_json', content)
        await self.channel_layer.group_send(
            self.room_group_name, content
        )

    def create_player(self, room_code, nickname, player_code):
        print("creating player", nickname)
        print('room_code', room_code)
        print('player_code', player_code)
        room = Room.objects.get(room_code=room_code)
        player = Player.objects.update_or_create(room=room, nickname=nickname, player_code=player_code)[0]
        print('created player nickname ->', player.nickname)
        print('created player code ->', player.player_code)
        self.player_code = player.player_code
        self.player_id = player.id

    async def send_question(self, event):
        event['player_code'] = self.player_code
        print('LOG$$$ CONSUMER send_question player_code', self.player_code)
        print('LOG$$$ CONSUMER send_question event', event)

        await self.send_json(event)

    async def send_shuffle_players_update(self, event):
        await self.send_json(event)

    async def send_waitroom_update(self, event):
        print('LOG$$$ CONSUMER send_waitroom_update player_code', self.player_code)
        print('LOG$$$ CONSUMER send_waitroom_update event', event)

        await self.send_json(event)

    async def send_message(self, event):
        event['players'] = []
        event['player_code'] = self.player_code
        event['player_id'] = self.player_id
        async for player in Player.objects.filter(room__room_code=self.room_code):
            event['players'].append({"nickname": player.nickname, "player_code": player.player_code})

        print('send_message', event)

        await self.send_json(event)
