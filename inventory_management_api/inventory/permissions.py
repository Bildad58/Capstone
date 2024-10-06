from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user
    
from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Modify this logic based on your needs
        return True  # Allow all users for demonstration purposes
    
