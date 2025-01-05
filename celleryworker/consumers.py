from datetime import  datetime
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from celery.result import AsyncResult
from .tasks import *


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'chat_{self.chat_id}'


        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)


    async def receive(self,text_data):

        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender = text_data_json['sender']
        receiver = text_data_json['receiver']


        task = save_message_task.apply_async(args=[self.chat_id, message, sender, receiver],countdown=1)

        await self.update_chat(self.chat_id, message)



        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'chat_message',
            'message': message,
            'sender': sender,
            'receiver': receiver,
            'task': task.id,
            'timestamp': str(datetime.now()),
        })


    async def chat_message(self,event):
        message = event['message']
        sender = event['sender']
        timestamp = event['timestamp']
        receiver = event['receiver']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'receiver': receiver,
            'timestamp': timestamp
        }))
    @sync_to_async
    def update_chat(self,chat_id,text):
        chat = Chat.objects.get(pk=chat_id)
        chat.last_message = text
        chat.save(update_fields=['last_message','last_changes'])


