from django.db import models
from django.contrib.auth.models import User
from django.core.validators import ValidationError

class Chat(models.Model):
    first_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='first_user')
    second_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='second_user')
    last_message = models.TextField(max_length=500,null=True,blank=True)
    last_changes = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f'{self.first_user} {self.second_user} {self.last_message}'


    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['first_user', 'second_user'],name='unique_chat'
            ),
        ]

    def save(self, *args, **kwargs):

        if self.first_user.id > self.second_user.id:
            self.first_user, self.second_user = self.second_user, self.first_user

        super().save(*args, **kwargs)


def file_validator(file):
    max_size_kb = 10240

    if file.size > max_size_kb:
        raise ValidationError(
            'File too large to upload.'
        )

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    text = models.TextField(max_length=500)
    file = models.FileField(upload_to='messages/', default=None,validators=[file_validator],null=True,blank=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='chat', null=True)
    date = models.DateTimeField(auto_now_add=True,null=True)





