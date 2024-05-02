from django.shortcuts import render
from rest_framework import viewsets,filters,generics
from .serializers import UserSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from apis.models import AppliedJobs,Job,CustomUser,Message
from apis.serializers import UserSerializer,AppliedJobsSerializer,JobSerializer,verifyOtpSerializer,MessageSerializer,ReceiverSerializer
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
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['location', 'type']
    
    
    @action(detail=False, methods=['get'])
    def posted_by_recruiter(self, request):
        # Retrieve the recruiter (authenticated user)
        recruiter = request.user
        
        # Filter jobs posted by the recruiter
        queryset = Job.objects.filter(recruiter=recruiter)
        serializer = self.get_serializer(queryset, many=True)
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['put'])
    def update_posted_by_recruiter(self, request, pk=None):
        # Retrieve the recruiter (authenticated user)
        recruiter = request.user
        
        # Get the job instance posted by the recruiter
        job = get_object_or_404(Job, pk=pk, recruiter=recruiter)
        
        # Serialize and update the job instance
        serializer = self.get_serializer(job, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'])
    def delete_posted_by_recruiter(self, request, pk=None):
        # Retrieve the recruiter (authenticated user)
        recruiter = request.user
        
        # Get the job instance posted by the recruiter
        job = get_object_or_404(Job, pk=pk, recruiter=recruiter)
        
        # Delete the job instance
        job.delete()
        return Response({'message': 'Job deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
    

    def get_queryset(self):
        # Get the current authenticated user
        user = self.request.user
        applied_job_ids = AppliedJobs.objects.filter(candidate=user).values_list('job__id', flat=True)
        queryset = Job.objects.exclude(id__in=applied_job_ids).exclude(recruiter=user)
        location = self.request.query_params.get('location')
        job_type = self.request.query_params.get('type')
        if location:
            queryset = queryset.filter(location__icontains=location)
        if job_type:
            queryset = queryset.filter(type__icontains=job_type)
        
        return queryset 

    def perform_create(self, serializer):
        # Assign the authenticated user as the recruiter of the job
        serializer.save(recruiter=self.request.user)
    
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

    if not email or not otp:
        return Response("Email and OTP are required", status=status.HTTP_400_BAD_REQUEST)


    serializer = verifyOtpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = get_object_or_404(CustomUser, email=email)
    print (user.otp)

    if not user.otp == int(otp):
        return Response("Incorrect OTP", status=status.HTTP_401_UNAUTHORIZED)

    user.is_verified = True
    user.save()

    return Response("OTP verified", status=status.HTTP_200_OK)

@api_view(['POST'])
def forgotPassword(request):
    email = request.data.get('email', None)
    if not email:
        return Response("Email is required", status=status.HTTP_400_BAD_REQUEST)
    user = get_object_or_404(CustomUser, email=email)
    forgot_password_email(email=user.email, name=user.username)
    return Response("Your Temporary Password is sended via Email", status=status.HTTP_200_OK)

class ChatListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        chat_id = self.request.data.get('chat_id')

        if not chat_id:
            return Message.objects.none()  # Return empty queryset if chat_id is not provided
        queryset = Message.objects.filter(chat_id=chat_id)

        return queryset


class ReceiverDetailsView(generics.ListAPIView):
    serializer_class = ReceiverSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get the authenticated user (sender)
        sender = self.request.user
        
        # Retrieve messages sent by the authenticated sender
        messages_sent_by_sender = Message.objects.filter(sender=sender)
        receivers_with_chat_ids = messages_sent_by_sender.values('receiver', 'chat_id').distinct()
        
        return receivers_with_chat_ids

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Prepare a list of receiver details with chat IDs
        serialized_data = []
        for item in queryset:
            receiver_id = item['receiver']
            chat_id = item['chat_id']
            
            # Retrieve receiver details from CustomUser model
            receiver = CustomUser.objects.get(pk=receiver_id)
            
            # Serialize receiver details using UserSerializer
            receiver_serializer = UserSerializer(receiver)
            receiver_data = {
                'receiver_details': receiver_serializer.data,
                'chat_id': chat_id
            }
            serialized_data.append(receiver_data)
        
        return Response(serialized_data)