from rest_framework import serializers
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'user_type', 'first_name', 'last_name', 'email', 'phone_number', 'address', 'profile_picture', 'created_at']
