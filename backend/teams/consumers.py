import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Team, ChatMessage

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.team_id = self.scope['url_route']['kwargs']['team_id']
        self.room_group_name = f'chat_{self.team_id}'
        self.user = self.scope['user']

        if self.user.is_anonymous or not await self.is_member(self.user, self.team_id):
            await self.close()
        else:
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        new_message = await self.save_message(self.user, self.team_id, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': self.user.username,
                'timestamp': str(new_message.timestamp),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'timestamp': event['timestamp'],
        }))

    @database_sync_to_async
    def is_member(self, user, team_id):
        return Team.objects.get(id=team_id).members.filter(id=user.id).exists()

    @database_sync_to_async
    def save_message(self, user, team_id, message):
        team = Team.objects.get(id=team_id)
        return ChatMessage.objects.create(user=user, team=team, message=message)
