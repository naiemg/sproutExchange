from django.contrib import admin
from apps.userauth.models import UserProfile, FarmerProfile, Address

admin.site.register(UserProfile)
admin.site.register(FarmerProfile)
admin.site.register(Address)