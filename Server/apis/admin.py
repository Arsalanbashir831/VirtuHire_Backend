from django.contrib import admin

# Register your models here.
from .models import Job,AppliedJobs,CustomUser,Message


admin.site.register(CustomUser)
admin.site.register(Job)
admin.site.register(AppliedJobs)
admin.site.register(Message)
