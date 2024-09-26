from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password','first_name',
        'last_name', 'mobile_number', 'address', 'profile_picture', 'bio']
        extra_kwargs = {'password': {'write_only':True}}

     
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        return super().update(instance, validated_data)   
