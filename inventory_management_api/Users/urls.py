from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.UserListCreateView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('profile/', views.ProfileListCreateView.as_view(), name='profile-list-create'),
    path('profile/<int:pk>/', views.ProfileDetailView.as_view(), name='profile-detail'),
    path('user-profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('register/', views.RegistrationView.as_view(), name='register'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
]