# from django.contrib.auth.models import User
from rest_framework import serializers, viewsets
from apis.models import Job,AppliedJobs,CustomUser
from django.contrib.auth.hashers import make_password

# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name','profile','is_verified','password']
    def create(self, validated_data):
        # Do not hash the password, store it as plain text
        return super().create(validated_data)


class JobSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Job
        fields = "__all__"

class AppliedJobsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AppliedJobs
        fields = "__all__"


class verifyOtpSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CustomUser
        fields = [ 'email','otp']
    def update(self, instance, validated_data):
        instance.is_verified = True
        instance.save()
        return instance
