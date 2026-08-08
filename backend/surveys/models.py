from django.db import models
# Create your models here.

class Response(models.Model):
    id = models.AutoField(primary_key=True)
    response_type = models.CharField(max_length=100)
    response_answers = models.JSONField()
    response_results = models.JSONField()
    response_date = models.DateField()
    response_time = models.TimeField()
    response_duration = models.DurationField(null=True, blank=True)