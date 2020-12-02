from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address_line_one = models.CharField(max_length=255)
    address_line_two = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    zipcode = models.IntegerField()
    telephone = models.CharField(max_length=20)
    is_farmer = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.username

class FarmerProfile(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    bio = models.TextField()

    def __str__(self):
        return self.user_profile.username