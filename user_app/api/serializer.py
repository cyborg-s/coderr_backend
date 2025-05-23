from rest_framework import serializers
from django.contrib.auth.models import User

from ..models import UserProfile

class NestedUserSerializer(serializers.ModelSerializer):
    """
    A simple serializer for the User model that serializes only the 'id'.
    Can be used to represent nested user references.
    """
    class Meta:
        model = User
        fields = ['id']

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserProfile model including nested fields
    from the related User model.

    Fields:
    - user: ID of the related User object (read-only)
    - type: user_type of the profile (CharField, based on user_type in profile)
    - username: username of the User (read-only)
    - email: email of the User (read/write)
    - remaining fields from UserProfile (first_name, last_name, tel, etc.)
    """
    user = serializers.IntegerField(source='user.id', read_only=True)
    type = serializers.CharField(source='user_type')
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source="user.email")

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'username',
            'user',
            'type',
            'first_name',
            'last_name',
            'tel',
            'file',
            'location',
            'email',
            'created_at',
            'description',
            'working_hours',
        ]

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        return instance
