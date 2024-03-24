from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    profile = models.ImageField(upload_to='profile_pics', blank=True)
    is_verified = models.BooleanField(default=False)
    otp = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return f'{self.username} Verified: {self.is_verified}' 

class Job(models.Model):
    recruiter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=None)
    job_title = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=100, blank=True)
    start_date = models.DateField(blank=True)
    end_date = models.DateField(blank=True)
    description = models.TextField(blank=True)
    job_document = models.FileField(upload_to='Jobs',blank=True)

    def __str__(self):
        return f'{self.recruiter.username} Job'

class AppliedJobs(models.Model):
    candidate = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=None)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    applied_date = models.DateField(blank=True)
    resume = models.FileField(upload_to='resume', blank=True)
    score = models.FloatField(blank=True)

    def __str__(self):
        return f'{self.candidate.username} AppliedJobs'
