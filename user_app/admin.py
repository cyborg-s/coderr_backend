from django.contrib import admin

from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'first_name', 'last_name', 'user_type', 
        'tel', 'location', 'created_at'
    ]
    list_filter = ['user_type', 'created_at']
    search_fields = ['first_name', 'last_name', 'user__username', 'location', 'description']
    readonly_fields = ['created_at']
