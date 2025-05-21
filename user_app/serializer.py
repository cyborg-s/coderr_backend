from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile

class NestedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id']

class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='user.id', read_only=True)
    type = serializers.CharField(source='user_type')
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'user', 'type', 'first_name', 'last_name', 'tel','file', 'location', 'email', 'created_at', 'description', 'working_hours']