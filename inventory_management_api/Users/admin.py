from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

class MyUserAdmin(UserAdmin):
    list_display = ('email', 'is_staff', 'is_active',)  # Fields to display in the admin list view
    list_filter = ('email', 'is_staff', 'is_active',)   # Filters available in the admin list view
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),      # Basic info section in user edit form
        ('Permissions', {'fields': ('is_staff', 'is_active')}),  # Permissions section in user edit form
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),                       # Make the form wider
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),                                              # Fields in the user creation form
    )
    
    search_fields = ('email',)     # Enable searching users by email
    ordering = ('email',)          # Default ordering of users in the admin

admin.site.register(CustomUser, MyUserAdmin)  # Register CustomUser with custom admin class
admin.site.register(profile)                  # Register profile model