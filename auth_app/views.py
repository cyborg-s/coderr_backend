

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
            first_name=request.data.get('first_name',''),
            last_name=request.data.get('last_name',''),
            user_type=request.data.get('type'),
            phone_number=request.data.get('phone_number', ''),
            address=request.data.get('address', ''),
        )
        profile.save()
        return Response({
                'token': token.key,
                'username': user.username,
                'email': user.email,
                'user_id': user.id
            }, status=status.HTTP_201_CREATED)
    else:
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    if request.method == 'POST':
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)