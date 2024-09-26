from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=100, blank=False, null=False)
    last_name = models.CharField(max_length=100, blank=False, null=False)  
    phone_number = models.CharField(max_length=20, blank=False, null=False)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to= 'profile_photos/',  blank=True, null=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.username