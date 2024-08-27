from django.db import models

class UploadedFiles(models.Model):
    id = models.AutoField(primary_key=True)
    session_token_id = models.IntegerField()
    file_path = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_path} uploaded at {self.uploaded_at}"