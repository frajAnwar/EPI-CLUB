import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import DirectMessage, Conversation
from django.contrib.auth.models import User

class MessagingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_anonymous:
            await self.close()
        else:
            self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
            self.conversation_group_name = f'conversation_{self.conversation_id}'

            await self.channel_layer.group_add(
                self.conversation_group_name,
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.conversation_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        new_message = await self.create_message(message)

        await self.channel_layer.group_send(
            self.conversation_group_name, {
                'type': 'chat_message',
                'message': new_message
            }
        )

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))

    @sync_to_async
    def create_message(self, message):
        conversation = Conversation.objects.get(id=self.conversation_id)
        new_message = DirectMessage.objects.create(
            sender=self.user,
            conversation=conversation,
            content=message
        )
        from .serializers import DirectMessageSerializer
        return DirectMessageSerializer(new_message).data
