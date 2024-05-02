import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from .models import CustomUser, Message
from asgiref.sync import sync_to_async
from rest_framework.authtoken.models import Token

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        headers = dict(self.scope['headers'])
        auth_header_bytes = headers.get(b'authorization', b'')
        auth_header = auth_header_bytes.decode() if auth_header_bytes else ''

        if not auth_header.startswith('Token '):
            await self.close()
            return
        
        token = auth_header[len('Token '):].strip()
        user = await self.authenticate_user(token)

        if not user:
            await self.close()
            return

        self.sender = user

        # Extract chat_id from query parameters (if needed)
        query_params = dict(pair.split('=') for pair in self.scope['query_string'].decode().split('&') if '=' in pair)
        chat_id = query_params.get('chat_id')

        if not chat_id:
            await self.close()
            return

        self.chat_id = chat_id
        self.room_name = f"chat_{self.chat_id}"

        await self.channel_layer.group_add(self.room_name, self.channel_name)

        # Send previous messages upon connection
        await self.send_previous_messages()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_name'):
            await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_content = data.get('message', '')
        receiver_id = data.get('receiver_id', None)  # Extract receiver_id from the incoming data

        if message_content and receiver_id:
            await self.save_message(self.sender.id, receiver_id, message_content)
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'chat.message',
                    'sender_id': self.sender.id,
                    'receiver_id': receiver_id,  # Include receiver_id in the message
                    'message': message_content,
                    'timestamp': str(timezone.now())
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat.message',
            'sender_id': event['sender_id'],
            'receiver_id': event['receiver_id'],  # Send receiver_id along with the message
            'message': event['message'],
            'timestamp': event['timestamp']
        }))

    @sync_to_async
    def authenticate_user(self, token):
        try:
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            return user
        except Token.DoesNotExist:
            return None

    @sync_to_async
    def save_message(self, sender_id, receiver_id, content):
        sender = CustomUser.objects.get(id=sender_id)
        receiver = CustomUser.objects.get(id=receiver_id)
        message = Message(sender=sender, receiver=receiver, content=content, chat_id=self.chat_id)
        message.save()

    @sync_to_async
    def fetch_room_messages(self):
        messages = Message.objects.filter(chat_id=self.chat_id).order_by('timestamp')
        return list(messages)  # Convert queryset to list

    async def send_previous_messages(self):
        messages = await self.fetch_room_messages()
        for message in messages:
            await self.chat_message({
                'sender_id': message.sender.id,
                'receiver_id': message.receiver.id,
                'message': message.content,
                'timestamp': str(message.timestamp)
            })
