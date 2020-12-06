from django.db import models
from django.contrib.auth.models import User
from address.models import AddressField

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telephone = models.CharField(max_length=20)
    is_farmer = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.username

class FarmerProfile(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    bio = models.TextField()

    def __str__(self):
        return self.user_profile.username

class Address(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    address = AddressField(on_delete=models.CASCADE)

    def __str__(self):
        return str(self.address)
