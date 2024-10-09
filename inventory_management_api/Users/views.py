# Import necessary modules and classes from Django REST framework
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CustomUser, profile  # Import models
from .serializers import CustomUserSerializer, ProfileSerializer, UserProfileSerializer  # Import serializers

# View for listing and creating users
class UserListCreateView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()  # Get all users from the database
    serializer_class = CustomUserSerializer  # Serializer for user data
    permission_classes = [permissions.IsAdminUser]  # Only admin users can access this view

# View for retrieving, updating, and deleting a specific user
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()  # Get all users from the database
    serializer_class = CustomUserSerializer  # Serializer for user data
    permission_classes = [permissions.IsAdminUser]  # Only admin users can access this view

# View for listing and creating profiles
class ProfileListCreateView(generics.ListCreateAPIView):
    queryset = profile.objects.all()  # Get all profiles from the database
    serializer_class = ProfileSerializer  # Serializer for profile data
    permission_classes = [permissions.IsAuthenticated]  # Any authenticated user can access this view

    def get_queryset(self):
        # Override the default queryset to return only the profiles created by the requesting user
        return profile.objects.filter(create_by=self.request.user)

    def perform_create(self, serializer):
        # Automatically set the user as the creator when creating a new profile
        serializer.save(create_by=self.request.user)

# View for retrieving, updating, and deleting a specific profile
class ProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = profile.objects.all()  # Get all profiles from the database
    serializer_class = ProfileSerializer  # Serializer for profile data
    permission_classes = [permissions.IsAuthenticated]  # Any authenticated user can access this view

    def get_queryset(self):
        # Override the default queryset to return only the profiles created by the requesting user
        return profile.objects.filter(create_by=self.request.user)

# View for retrieving and updating the authenticated user's profile
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer  # Serializer for user profile data
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can access this view

    def get_object(self):
        # Return the current authenticated user
        return self.request.user

# View for user registration
class RegistrationView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()  # Get all users from the database
    serializer_class = UserProfileSerializer  # Serializer for user registration data
    permission_classes = [permissions.AllowAny]  # Anyone can access this view for registration

    def create(self, request, *args, **kwargs):
        # Get the data from the request and validate it using the serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Raise an exception if validation fails
        user = serializer.save()  # Save the new user if validation passes
        headers = self.get_success_headers(serializer.data)  # Get the success headers
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)  # Return the created user data

# View for changing the password of the authenticated user
class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can access this view

    def post(self, request):
        user = request.user  # Get the currently authenticated user
        old_password = request.data.get('old_password')  # Retrieve the old password from the request
        new_password = request.data.get('new_password')  # Retrieve the new password from the request

        # Check if the provided old password is correct
        if not user.check_password(old_password):
            return Response({'detail': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)  # Return an error if the old password is wrong

        # Set and save the new password for the user
        user.set_password(new_password)
        user.save()
        return Response({'detail': 'Password changed successfully.'}, status=status.HTTP_200_OK)  # Return a success message after password change
