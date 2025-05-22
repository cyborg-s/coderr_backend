from django.contrib import admin

from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'first_name', 'last_name', 'user_type', 'location', 'created_at']
    search_fields = ['user__username', 'first_name', 'last_name', 'location']
    list_filter = ['user_type', 'location', 'created_at']
    readonly_fields = ['created_at']
