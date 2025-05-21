from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import UserProfile
from .serializer import UserProfileSerializer
from django.shortcuts import get_object_or_404

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_profile(request, pk):
    try:
        profile = get_object_or_404(UserProfile, user_id=pk)
    except Exception:
        return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def business_profiles(request):
    profiles = UserProfile.objects.filter(user_type=UserProfile.BUSINESS)
    serializer = UserProfileSerializer(profiles, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def customer_profiles(request):
    profiles = UserProfile.objects.filter(user_type=UserProfile.CUSTOMER)
    serializer = UserProfileSerializer(profiles, many=True)
    return Response(serializer.data)