# from django.contrib.auth.models import User
from rest_framework import serializers, viewsets
from apis.models import Job,AppliedJobs,CustomUser,Message
from django.contrib.auth.hashers import make_password

# Serializers define the API representation.
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name','profile','is_verified','password']
        extra_kwargs = {
            'username': {'required': False},
            'password': {'required': False, 'write_only': True}
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class JobSerializer(serializers.ModelSerializer):
    recruiter = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    recruiter_details = UserSerializer(source='recruiter', read_only=True)
    class Meta:
        model = Job
        fields = "__all__"
        # fields = ['id', 'recruiter', 'title', 'company', 'type','location','postedDate','responsibilities','experience','skills','job_document','recruiter_details','education']

class AppliedJobsSerializer(serializers.ModelSerializer):
    candidate = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    job = serializers.PrimaryKeyRelatedField(queryset=Job.objects.all())
    candidate_details = UserSerializer(source='candidate', read_only=True)
    job_details = JobSerializer(source='job', read_only=True)
    class Meta:
        model = AppliedJobs
        fields = "__all__"
        


class verifyOtpSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [ 'email','otp']
    def update(self, instance, validated_data):
        instance.is_verified = True
        instance.save()
        return instance

class MessageSerializer(serializers.ModelSerializer):
    sender = CustomUser
    receiver = CustomUser

    class Meta:
        model = Message
        fields = ['sender', 'receiver', 'content', 'timestamp','chat_id']
        
        
class ReceiverSerializer(serializers.Serializer):
    receiver = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    chat_id = serializers.CharField()

        
