from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings 

class UserManager(BaseUserManager):
    def create_user(self, username, email, password, **other_fields):
        # Validate that username and email are provided
        if not username:
            raise ValueError('Username must be provided')
        if not email:
            raise ValueError('Email must be provided')
        
        if not password:
            raise ValueError('password must be provided')
        
        # Create a new user instance
        user = self.model(username=username, email=self.normalize_email(email), **other_fields)
        user.set_password(password)  # Hash the password
        user.save(using=self._db)  # Save the user to the database
        return user 
    
    def create_superuser(self, username, email, password, **other_fields):
        # Set default values for superuser fields
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)
        
        # Ensure superuser has necessary permissions
        if other_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        # Create and return the superuser
        user = self.create_user(username, email, password, **other_fields)
        user.save(using=self._db)
        return user

class CustomUser(AbstractUser):
    # Custom User model with email as the unique identifier
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    email = models.EmailField(max_length=150, unique=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'  # Use email for authentication instead of username
    REQUIRED_FIELDS = []  # Email and password are required by default
    
    def __str__(self):
        return self.email

class profile(models.Model):
    # One-to-one relationship with the custom user model
    create_by = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)  
    first_name = models.CharField(max_length=100, blank=False, null=False)
    last_name = models.CharField(max_length=100, blank=False, null=False)   
    phone_number = models.CharField(max_length=20, blank=False, null=False)
    address = models.TextField(blank=True, null=True)   
    profile_picture = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True)  
    created = models.DateTimeField(auto_now_add=True)  # Automatically set when object is created
    updated = models.DateTimeField(auto_now=True)  # Automatically updated on each save

    def __str__(self):
        return self.first_name