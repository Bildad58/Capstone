from rest_framework import serializers
from .models import CustomUser, profile
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id',  'password', 'email', 'is_staff', 'is_active']  # Fields to include in serialization
        extra_kwargs = {'password': {'write_only': True}}  # Ensure password is write-only

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
        

    def update(self, instance, validated_data):
        # Custom update method to properly handle password updates
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        return super().update(instance, validated_data)

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = profile
        fields = ['id', 'create_by', 'first_name', 'last_name', 'phone_number',
                  'address', 'profile_picture', 'bio', 'created', 'updated']  # All fields included

    def to_representation(self, instance):
        # Custom representation to include user email
        representation = super().to_representation(instance)
        representation['user_email'] = instance.create_by.email if instance.create_by else None
        return representation

class UserProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False)  # Nested serializer for profile

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'password', 'email', 'is_staff', 'is_active', 'profile']  # Include profile
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', None)
        user = CustomUser.objects.create_user(**validated_data)
        if profile_data:
            profile.objects.create(create_by=user, **profile_data)
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        # Update user fields
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()

        # Update or create profile
        if profile_data:
            profile_instance, created = profile.objects.get_or_create(create_by=instance)
            for attr, value in profile_data.items():
                setattr(profile_instance, attr, value)
            profile_instance.save()

        return instance