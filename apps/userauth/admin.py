from django.contrib import admin
from apps.userauth.models import UserProfile, FarmerProfile

admin.site.register(UserProfile)
admin.site.register(FarmerProfile)