from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    photo = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True,null=True)
    is_online = models.BooleanField(default=False)
