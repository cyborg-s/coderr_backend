from rest_framework import serializers
from django.contrib.auth.models import User

from ..models import UserProfile

class NestedUserSerializer(serializers.ModelSerializer):
    """
    Ein einfacher Serializer für User-Model, der nur die 'id' serialisiert.
    Kann verwendet werden, wenn man User-Referenzen verschachtelt darstellen möchte.
    """
    class Meta:
        model = User
        fields = ['id']

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer für das UserProfile-Modell mit verschachtelten Feldern aus dem
    zugehörigen User-Modell.

    Felder:
    - user: ID des zugehörigen User-Objekts (read-only)
    - type: user_type des Profils (CharField, basiert auf user_type im Profil)
    - username: Username des Users (read-only)
    - email: Email des Users (read-only)
    - restliche Felder aus UserProfile (first_name, last_name, tel, etc.)
    """
    user = serializers.IntegerField(source='user.id', read_only=True)
    type = serializers.CharField(source='user_type')
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source="user.email")

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'username',   # User.username, read-only
            'user',       # User.id, read-only
            'type',       # UserProfile.user_type
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