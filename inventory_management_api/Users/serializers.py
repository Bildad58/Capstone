from rest_framework import serializers
from .models import CustomUser, profile
from django.contrib.auth import get_user_model

User = get_user_model()

# Serializer for CustomUser model
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id',  'password', 'email', 'is_staff', 'is_active']  # Fields to include in the serialized output
        extra_kwargs = {'password': {'write_only': True}}  # Ensure password is write-only

    # Custom create method to handle user creation, including password hashing
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)  # Creates the user using Django's create_user method
        return user

    # Custom update method to handle password updates separately
    def update(self, instance, validated_data):
        # If password is present in the validated data, handle it separately
        if 'password' in validated_data:
            password = validated_data.pop('password')  # Remove password from validated data
            instance.set_password(password)  # Use set_password to hash and save the new password
        return super().update(instance, validated_data)  # Proceed with default update logic for other fields

# Serializer for Profile model
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = profile
        fields = ['id', 'create_by', 'first_name', 'last_name', 'phone_number',
                  'address', 'profile_picture', 'bio', 'created', 'updated']  # Fields to include in the serialized output

    # Custom representation to include additional data in the serialized output
    def to_representation(self, instance):
        representation = super().to_representation(instance)  # Get the default representation
        representation['user_email'] = instance.create_by.email if instance.create_by else None  # Include the user's email if available
        return representation  # Return the modified representation

# Serializer for the CustomUser model including a nested profile serializer
class UserProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False)  # Include the ProfileSerializer for nested profile data

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'password', 'email', 'is_staff', 'is_active', 'profile']  # Include profile field in the serialized output
        extra_kwargs = {'password': {'write_only': True}}  # Make password write-only

    # Custom create method to handle user and profile creation
    def create(self, validated_data):
        profile_data = validated_data.pop('profile', None)  # Extract profile data if provided
        user = CustomUser.objects.create_user(**validated_data)  # Create the user
        if profile_data:
            # If profile data exists, create a profile linked to the user
            profile.objects.create(create_by=user, **profile_data)
        return user

    # Custom update method to handle both user and profile updates
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)  # Extract profile data if provided

        # Update user fields
        for attr, value in validated_data.items():
            if attr == 'password':  # Handle password separately
                instance.set_password(value)  # Hash and set the new password
            else:
                setattr(instance, attr, value)  # Update other user attributes
        instance.save()  # Save the updated user instance

        # Update or create profile if profile data is provided
        if profile_data:
            profile_instance, created = profile.objects.get_or_create(create_by=instance)  # Get or create the profile
            for attr, value in profile_data.items():
                setattr(profile_instance, attr, value)  # Update profile fields
            profile_instance.save()  # Save the updated profile instance

        return instance  # Return the updated user instance
