import json
from django.utils import timezone
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from rest_framework.authtoken.models import Token
from channels.layers import get_channel_layer
from .models import Message, CustomUser  # Ensure CustomUser is correctly imported
from channels.db import database_sync_to_async
from django.db.models import Q

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = None
        self.room_group_name = None

        # Extract the token from the query string
        token = self.scope['query_string'].decode().split('=')[1]
        self.user = await self.get_user_by_token(token)

        if not self.user:
            await self.close()
        else:
            self.room_group_name = f"chat_{self.user.id}"
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        if self.room_group_name:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        command = text_data_json.get('command', '')

        if command == 'fetch_messages':
            receiver_id = text_data_json['receiver_id']
            # Fetch messages where either the current user is the sender or the receiver
            messages = await self.fetch_messages(self.user.id, receiver_id)
            await self.send(text_data=json.dumps({
                'status': 'success',
                'messages': messages
            }))
        elif command == 'send_message':
            message_content = text_data_json['message']
            receiver_id = text_data_json['receiver_id']
            sender_id = text_data_json['sender_id']

            # Store the message in the database
            message = await self.store_message(sender_id, receiver_id, message_content)

            # Get receiver channel group name
            receiver_group_name = f"chat_{receiver_id}"
            
            # Get the current timestamp
            timestamp = timezone.now().isoformat()

            # Forward the message to the receiver's group
            await self.channel_layer.group_send(
                receiver_group_name,
                {
                    'type': 'chat_message',
                    'message': message_content,
                    'sender_id': sender_id,
                    'receiver_id': receiver_id,
                    'timestamp': timestamp
                }
            )

            # Send a response back to the sender
            await self.send(text_data=json.dumps({
                'status': 'success',
                'message': message_content,
                'receiver_id': receiver_id,
                'timestamp': timestamp,
                'message_id': message.id,
                "sender_id":sender_id
            }))
        else:
            await self.send(text_data=json.dumps({
                'status': 'error',
                'message': 'Invalid command'
            }))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'timestamp': event['timestamp']
        }))

    @sync_to_async
    def get_user_by_token(self, token):
        try:
            token_obj = Token.objects.get(key=token)
            return token_obj.user
        except Token.DoesNotExist:
            return None

    @sync_to_async
    def store_message(self, sender_id, receiver_id, content):
        sender = CustomUser.objects.get(id=sender_id)
        receiver = CustomUser.objects.get(id=receiver_id)
        message = Message.objects.create(sender=sender, receiver=receiver, content=content)
        return message

    async def fetch_messages(self, user_id, other_user_id):
        # Call the synchronous ORM operation wrapped in database_sync_to_async
        messages = await database_sync_to_async(self.get_messages)(user_id, other_user_id)
        return messages

    def get_messages(self, user_id, other_user_id):
        # Fetch messages, ensuring datetime is serialized
        messages = Message.objects.filter(
            Q(sender_id=user_id, receiver_id=other_user_id) |
            Q(sender_id=other_user_id, receiver_id=user_id)
        ).order_by('timestamp').values(
            'id', 'sender_id', 'receiver_id', 'content', 'timestamp'
        )
        
        # Convert datetime objects to strings for JSON serialization
        messages_list = list(messages)
        for message in messages_list:
            message['timestamp'] = message['timestamp'].isoformat() if message['timestamp'] else None

        return messages_list
