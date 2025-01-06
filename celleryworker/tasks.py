from celery import shared_task
from django.contrib.auth import get_user_model

from celleryworker.models import Chat, Message


@shared_task
def save_message_task(chat_id,text,sender_id,receiver_id):
    try:
        chat = Chat.objects.get(id=chat_id)
        sender = get_user_model().objects.get(id=sender_id)
        receiver = get_user_model().objects.get(id=receiver_id)

        message = Message.objects.create(chat=chat, text=text, sender=sender, receiver=receiver)


        return message.id
    except Exception as e:
        print(f"Error in save_message_task: {e}")
        return None