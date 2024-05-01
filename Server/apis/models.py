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
    TYPE_CHOICES = [
        ('Full Time', 'full_time'),
        ('Part Time', 'part_time'),
        ('Contract', 'contract'),
        ('Freelance', 'freelance'),
    ]
    TYPE_LOCATION = [
        ('Remote', 'remote'),
        ('On Site', 'onsite'),   
    ]
    SKILLS_DELIMITER = ','
    id = models.AutoField(primary_key=True)
    recruiter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=None)
    title = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)
    type = models.CharField(max_length=100, choices=TYPE_CHOICES, blank=True)
    location = models.CharField(max_length=100, choices=TYPE_LOCATION, blank=True)
    postedDate = models.DateField(auto_now=True)
    responsibilities = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    skills = models.TextField(blank=True)
    education = models.TextField(blank=True)
    job_document = models.FileField(upload_to='Jobs',blank=True)

    # Set skills as a list
    def set_skills(self, skills_list):
        self.skills = self.SKILLS_DELIMITER.join(skills_list)

    # Get skills as a list
    def get_skills(self):
        return self.skills.split(self.SKILLS_DELIMITER) if self.skills else []
    

    def __str__(self):
        return f'{self.recruiter.username} Job'

class AppliedJobs(models.Model):
    candidate = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=None)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    applied_date = models.DateField(blank=True)
    resume = models.FileField(upload_to='resume', blank=True)
    avg_score = models.FloatField(blank=True , default=None)
    experience_score = models.FloatField(blank=True , default=None)
    description_score = models.FloatField(blank=True , default=None) 
    education_score = models.FloatField(blank=True , default=None) 
    skills_score = models.FloatField(blank=True , default=None) 
    domain_score = models.FloatField(blank=True , default=None) 
   
    def __str__(self):
        return f'{self.candidate.username} AppliedJobs'


class Message(models.Model):
    sender = models.ForeignKey(
        CustomUser,
        related_name='sent_messages',
        on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        CustomUser,
        related_name='received_messages',
        on_delete=models.CASCADE
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender} -> {self.receiver}: {self.content}'