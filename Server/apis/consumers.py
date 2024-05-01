import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from .models import CustomUser, Message
from asgiref.sync import sync_to_async
from rest_framework.authtoken.models import Token

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        headers = dict(self.scope['headers'])  # Convert headers list to a dictionary
        auth_header_bytes = headers.get(b'authorization', b'')  # Get the Authorization header as bytes
        auth_header = auth_header_bytes.decode() if auth_header_bytes else ''

        if not auth_header.startswith('Token '):
            await self.close()
            return
        
        token = auth_header[len('Token '):].strip()  # Extract the token value
        user = await self.authenticate_user(token)

        if not user:
            await self.close()
            return

        self.sender = user

        # Extract receiver_id from query parameters
        query_params = dict(pair.split('=') for pair in self.scope['query_string'].decode().split('&') if '=' in pair)
        receiver_id = query_params.get('receiver_id')

        if not receiver_id:
            await self.close()
            return

        self.receiver_id = receiver_id
        self.room_name = self.get_room_name(self.sender.id, self.receiver_id)

        await self.channel_layer.group_add(self.room_name, self.channel_name)

    async def disconnect(self, close_code):
        if hasattr(self, 'room_name'):
            await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_content = data.get('message', '')

        if message_content:
            await self.save_message(self.sender.id, self.receiver_id, message_content)
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'chat.message',
                    'sender_id': self.sender.id,
                    'sender_username': self.sender.username,
                    'message': message_content,
                    'timestamp': str(timezone.now())
                }
            )

    async def chat_message(self, event):
        sender_id = event['sender_id']
        message = event['message']
        timestamp = event['timestamp']

        await self.send(text_data=json.dumps({
            'type': 'chat.message',
            'sender_id': sender_id,
            'message': message,
            'timestamp': timestamp
        }))

    @sync_to_async
    def authenticate_user(self, token):
        try:
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            return user
        except Token.DoesNotExist:
            return None

    @staticmethod
    def get_room_name(sender_id, receiver_id):
        # Convert sender_id and receiver_id to integers if they are not already
        sender_id = int(sender_id)
        receiver_id = int(receiver_id)

        # Create a unique room name based on sorted sender and receiver IDs
        room_name = f"chat_{min(sender_id, receiver_id)}_{max(sender_id, receiver_id)}"
        return room_name

    @sync_to_async
    def save_message(self, sender_id, receiver_id, content):
        sender = CustomUser.objects.get(id=sender_id)
        receiver = CustomUser.objects.get(id=receiver_id)
        message = Message(sender=sender, receiver=receiver, content=content)
        message.save()
