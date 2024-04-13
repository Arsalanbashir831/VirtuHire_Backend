from django.shortcuts import render
from rest_framework import viewsets
from .serializers import UserSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from apis.models import AppliedJobs,Job,CustomUser
from apis.serializers import UserSerializer,AppliedJobsSerializer,JobSerializer,verifyOtpSerializer
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import check_password,make_password
from rest_framework.decorators import action
from apis.email import send_otp_via_email,forgot_password_email

@api_view(['POST'])
def login(request):
    username = request.data.get('username', None)
    password = request.data.get('password', None)
    if not username or not password:
        return Response("Username and password are required", status=status.HTTP_400_BAD_REQUEST)
    user = get_object_or_404(CustomUser, username=username)
    print(make_password(password))
    if not user.password == password:
        return Response("Incorrect password", status=status.HTTP_401_UNAUTHORIZED)
    token, created = Token.objects.get_or_create(user=user)
    serializer_context = {'request': request}

    serializer = UserSerializer(user, context=serializer_context)
    return Response({'token': token.key, 'user': serializer.data})



# Testing Token Authentication
@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def userData(request):
    data ={
        'id': request.user.id,
        'username': request.user.username,
        'email': request.user.email,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'is_verified': request.user.is_verified,
    }
    return Response(data,status=status.HTTP_200_OK)


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]


class AppliedJobsViewSet(viewsets.ModelViewSet):
    queryset = AppliedJobs.objects.all()
    serializer_class = AppliedJobsSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Custom action to retrieve all jobs applied by a specific candidate
    @action(detail=True, methods=['get'])
    def get_jobs(self, request, pk=None):
        queryset = AppliedJobs.objects.filter(candidate=pk)
        serializer = AppliedJobsSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    # Custom action to retrieve all candidates who applied for a specific job
    @action(detail=True, methods=['get'])
    def get_candidate(self, request, pk=None):
        queryset = AppliedJobs.objects.filter(job=pk)
        serializer = AppliedJobsSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    # Override create method to enforce unique candidate constraint
    def create(self, request, *args, **kwargs):
        candidate_id = request.data.get('candidate')
        job_id = request.data.get('job')

        # Check if the candidate has already applied for the job
        if AppliedJobs.objects.filter(candidate=candidate_id, job=job_id).exists():
            return Response({'error': 'Candidate has already applied for this job'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer

    @action(detail=True, methods=['get'])
    def get_job_posting(self, request, pk=None):
        queryset = Job.objects.filter(recruiter=pk)
        serializer = JobSerializer(queryset, many=True,context={'request': request}) 
        return Response(serializer.data)
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]



@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()

        # Use filter instead of get to handle multiple users with the same email
        existing_users = CustomUser.objects.filter(email=user.email)

        if existing_users.exists():
            # Assuming you want to select the latest user if there are multiple
            latest_user = existing_users.latest('id')

            data = {
                'id': latest_user.id,
                'username': latest_user.username,
                'email': latest_user.email,
                'first_name': latest_user.first_name,
                'last_name': latest_user.last_name,
                'is_verified': latest_user.is_verified,
                'message': 'Signup successful'
            }

            send_otp_via_email(email=latest_user.email, name=latest_user.username)
            return Response(data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def verify_otp(request):
    email = request.data.get('email', None)
    otp = request.data.get('otp', None)
    
    # Check if email and otp are provided in the request data
    if not email or not otp:
        return Response("Email and OTP are required", status=status.HTTP_400_BAD_REQUEST)

    # Validate the request data using the serializer
    serializer = verifyOtpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    # Get the user object by email or return 404 if not found
    user = get_object_or_404(CustomUser, email=email)
    print (user.otp)
    
    # Check if the provided OTP matches the user's OTP
    if not user.otp == int(otp):
        return Response("Incorrect OTP", status=status.HTTP_401_UNAUTHORIZED)

    # Update user verification status to True
    user.is_verified = True
    user.save()

    # Return success response
    return Response("OTP verified", status=status.HTTP_200_OK)

@api_view(['POST'])
def forgotPassword(request):
    email = request.data.get('email', None)
    if not email:
        return Response("Email is required", status=status.HTTP_400_BAD_REQUEST)
    user = get_object_or_404(CustomUser, email=email)
    forgot_password_email(email=user.email, name=user.username)
    return Response("Your Temporary Password is sended via Email", status=status.HTTP_200_OK)
