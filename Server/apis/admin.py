from django.contrib import admin

# Register your models here.
from .models import Job,AppliedJobs,CustomUser


admin.site.register(CustomUser)
admin.site.register(Job)
admin.site.register(AppliedJobs)
