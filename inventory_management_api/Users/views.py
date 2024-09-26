from django.shortcuts import render
from rest_framework import Viewsets, permissions
from .serializers import UserSerializer
from django.contrib.auth import get_user_model 

User = get_user_model()

class UserViewset(Viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self): 
        if self.action == 'create':
            return [permissions.AllowAny]
        return [permissions.IsAuthenticated]    

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=user.id) 