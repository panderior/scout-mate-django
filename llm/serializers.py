from rest_framework import serializers
from .models import JobRequirementModel, MatrixScoresModel, MatrixWeightsModel
from authenticate.serializers import UserSessionSerializer
from files.serializers import UploadedFileSerializer

class MatrixWeightsSerializer(serializers.ModelSerializer):
    session = UserSessionSerializer(required=False)
    
    class Meta:
        model = MatrixWeightsModel
        fields = ('id', 'session','experiance_weight', 'relevance_weight', 'education_weight', 'skill_weight')

class MatrixScoresSerializer(serializers.ModelSerializer):
    uploaded_file = UploadedFileSerializer(required=False)

    class Meta:
        model = MatrixScoresModel
        fields = ('id', 'uploaded_file','experiance_score', 'relevance_score', 'education_score', 'skill_score', 'overall_score')

class JobRequirementSerializer(serializers.ModelSerializer):
    session = UserSessionSerializer(required=False)
    
    class Meta:
        model = JobRequirementModel
        fields = ('id', 'session', 'value', 'requirement_type')