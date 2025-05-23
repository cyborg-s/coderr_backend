from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from .serializer import UserSerializer, LoginSerializer
from user_app.models import UserProfile


@api_view(['POST'])
@permission_classes([AllowAny])
def registration(request):
    """
    Registration of a new user.

    Creates a new User, an associated UserProfile, and returns an auth token.

    Body parameters:
    - username (str)
    - email (str)
    - password (str)
    - first_name (str)
    - last_name (str)
    - phone_number (str)
    - address (str)
    - type (str): User role or type

    Response (201 Created):
    - token (str): Auth token
    - username (str)
    - email (str)
    - user_id (int)
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
        profile = UserProfile.objects.create(
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


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    User login.

    Expects valid credentials (username and password) and returns authentication data on success.

    Body parameters:
    - username (str)
    - password (str)

    Response (200 OK):
    - token (str)
    - user_id (int)
    - username (str)
    """
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
