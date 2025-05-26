from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .serializer import UserSerializer, LoginSerializer
from user_app.models import UserProfile


class RegistrationView(APIView):
    """
    API endpoint for registering a new user.

    POST:
    - Creates a new user account.
    - Generates an authentication token for the user.
    - Creates a related UserProfile with first_name, last_name, and user_type.

    Permissions:
    - AllowAny: This endpoint is publicly accessible.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handles user registration.

        Request body:
        {
            "username": "johndoe",
            "email": "john@example.com",
            "password": "securepassword",
            "first_name": "John",
            "last_name": "Doe",
            "type": "customer"
        }

        Returns:
        - 201 Created: With token and user info.
        - 400 Bad Request: If data is invalid.
        """
        user_data = {
            "username": request.data.get("username"),
            "email": request.data.get("email"),
            "password": request.data.get("password")
        }
        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            UserProfile.objects.create(
                user=user,
                first_name=request.data.get('first_name', ''),
                last_name=request.data.get('last_name', ''),
                user_type=request.data.get('type'),
            )
            return Response({
                'token': token.key,
                'username': user.username,
                'email': user.email,
                'user_id': user.id
            }, status=status.HTTP_201_CREATED)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    API endpoint for logging in an existing user.

    POST:
    - Authenticates the user and returns a token and user data.

    Permissions:
    - AllowAny: This endpoint is publicly accessible.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handles user login.

        Request body:
        {
            "username": "johndoe",
            "password": "securepassword"
        }

        Returns:
        - 200 OK: With authentication token and user info.
        - 400 Bad Request: If credentials are invalid.
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
