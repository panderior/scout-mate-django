from django.db import models
from files.models import UploadedFileModel
from authenticate.models import UserSessionModel
from django.core.validators import MinValueValidator, MaxValueValidator
from .constants import EDUCATION, DOMAIN, SKILL
from django.utils import timezone


class MatrixWeightsModel(models.Model):
    session = models.ForeignKey(UserSessionModel, on_delete=models.CASCADE)
    experiance_weight = models.FloatField(default=0.25, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    relevance_weight = models.FloatField(default=0.25, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    education_weight = models.FloatField(default=0.25, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    skill_weight = models.FloatField(default=0.25, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    created_at = models.DateTimeField(default=timezone.now)

class MatrixScoresModel(models.Model):
    uploaded_file = models.ForeignKey(UploadedFileModel, on_delete=models.CASCADE)
    candidate_name = models.CharField(max_length=100)
    experiance_score = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    relevance_score = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    education_score = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    skill_score = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    overall_score = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        try:
            related_matrix_weights = MatrixWeightsModel.objects.get(session__id=self.uploaded_file.session.id)
            self.overall_score = self.experiance_score * related_matrix_weights.experiance_weight
            self.overall_score += self.relevance_score * related_matrix_weights.relevance_weight
            self.overall_score += self.education_score * related_matrix_weights.education_weight
            self.overall_score += self.skill_score * related_matrix_weights.skill_weight
        except Exception as exp:
            print(exp)

        super(MatrixScoresModel, self).save(*args, **kwargs)

class JobRequirementModel(models.Model):
    requirements_types_list = [
        (EDUCATION, EDUCATION),
        (DOMAIN, DOMAIN),
        (SKILL, SKILL)
    ]

    session = models.ForeignKey(UserSessionModel, on_delete=models.CASCADE)
    value = models.CharField(max_length=100)
    requirement_type = models.CharField(max_length=100, choices=requirements_types_list)
    created_at = models.DateTimeField(default=timezone.now)

