from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserSessionModel(models.Model):
    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(default=timezone.now)