from django.db import models
from authenticate.models import UserSessionModel
from django.utils import timezone


class UploadedFileModel(models.Model):
    session = models.ForeignKey(UserSessionModel, on_delete=models.CASCADE)
    file_path = models.CharField(max_length=500)
    uploaded_at = models.DateTimeField(default=timezone.now)
