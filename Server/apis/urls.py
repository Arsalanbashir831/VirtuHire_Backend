from django.contrib import admin
from django.urls import path,include
from rest_framework import routers

from . import views


routers = routers.DefaultRouter()

# routers.register('profile',views.ProfileViewSet)
routers.register('user',views.UserViewSet)
routers.register('job',views.JobViewSet)
routers.register('appliedjobs',views.AppliedJobsViewSet)



urlpatterns = [
   
    path('login', views.login),
    path('signup', views.signup),
    path('auth_user', views.userData),
    path('verify_otp', views.verify_otp),
    path('forgot_password', views.forgotPassword),
     path('chat_users', views.ReceiverDetailsView.as_view(), name='receiver-list'),
     path('update_password', views.update_password, name='update_password'),
    
    path('',include(routers.urls)),
  
    
]
