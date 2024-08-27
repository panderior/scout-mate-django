from rest_framework import serializers
from .models import UploadedFileModel
from authenticate.serializers import UserSessionSerializer

class UploadedFileSerializer(serializers.ModelSerializer):
    session = UserSessionSerializer(required=False)
    
    class Meta:
        model = UploadedFileModel
        fields = ('id', 'session','file_path')
