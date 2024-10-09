from django.urls import path
from . import views

urlpatterns = [
    # URL for listing all users or creating a new user
    # Maps to UserListCreateView for handling GET (list users) and POST (create a user) requests
    path('users/', views.UserListCreateView.as_view(), name='user-list-create'),

    # URL for retrieving, updating, or deleting a specific user by their primary key (pk)
    # Maps to UserDetailView for handling GET (retrieve), PUT/PATCH (update), and DELETE requests for a specific user
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),

    # URL for listing all profiles or creating a new profile
    # Maps to ProfileListCreateView for handling GET (list profiles) and POST (create a profile) requests
    path('profile/', views.ProfileListCreateView.as_view(), name='profile-list-create'),

    # URL for retrieving, updating, or deleting a specific profile by its primary key (pk)
    # Maps to ProfileDetailView for handling GET (retrieve), PUT/PATCH (update), and DELETE requests for a specific profile
    path('profile/<int:pk>/', views.ProfileDetailView.as_view(), name='profile-detail'),

    # URL for viewing and editing the authenticated user's profile
    # Maps to UserProfileView for handling requests related to the current logged-in user's profile
    path('user-profile/', views.UserProfileView.as_view(), name='user-profile'),

    # URL for user registration
    # Maps to RegistrationView for handling POST requests to register a new user
    path('register/', views.RegistrationView.as_view(), name='register'),

    # URL for changing the authenticated user's password
    # Maps to ChangePasswordView for handling POST requests to change the user's password
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
]
