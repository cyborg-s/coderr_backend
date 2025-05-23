from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for registering a new user.

    Fields:
    - username (str): Username
    - email (str): Email address
    - password (str): Password (write-only)
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        """
        Creates a new user with an encrypted password.
        """
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user authentication.

    Input:
    - username (str): Username
    - password (str): Password

    Output on success:
    - token (str): Authentication token
    - username (str)
    - email (str)
    - user_id (int)
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Validates the credentials and returns an auth token.
        """
        user = User.objects.filter(username=data['username']).first()
        if user is None:
            raise serializers.ValidationError("Invalid credentials.")

        password_correct = user.check_password(data['password'])
        if not password_correct:
            raise serializers.ValidationError("Invalid credentials.")

        token, created = Token.objects.get_or_create(user=user)

        return {
            'token': token.key,
            'username': user.username,
            'email': user.email,
            'user_id': user.id
        }
