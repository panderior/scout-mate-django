from rest_framework import serializers
from .models import UserSessionModel

class UserSessionSerializer(serializers.ModelSerializer):    
    class Meta:
        model = UserSessionModel
        fields = ('token', 'created_at')
