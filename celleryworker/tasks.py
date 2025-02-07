from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from celleryworker.models import Chat, Message
from MessengerDocker.settings import EMAIL_HOST_USER

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


@shared_task
def send_message_task(email,message):
    subject = "Message sent from Chat"
    from_email = EMAIL_HOST_USER
    recipient_list = [email]

    user = get_user_model().objects.get(email=email)

    credentials = {
        "username": user.username,
        "message": message,
    }

    html_content = render_to_string("index/email.html", credentials)

    email_message = EmailMessage(subject, html_content, from_email, recipient_list)
    email_message.content_subtype = 'html'
    email_message.send()

    return True




@shared_task
def send_bulk_message_task(user_emails,message):
    for user_email in user_emails:
        send_message_task.delay(user_email,message)

