from django.db import models
from authenticate.models import UserSessionModel
from .constants import SYSTEM, USER
from django.utils import timezone

class ChatMessageModel(models.Model):
    chat_user_types_list = [
        (SYSTEM, SYSTEM),
        (USER, USER)
    ]
    session = models.ForeignKey(UserSessionModel, on_delete=models.CASCADE) 
    chat_text = models.CharField(max_length=500)
    sender_type = models.CharField(max_length=100, choices=chat_user_types_list)
    reciever_type = models.CharField(max_length=100, choices=chat_user_types_list)
    created_at = models.DateTimeField(default=timezone.now)
