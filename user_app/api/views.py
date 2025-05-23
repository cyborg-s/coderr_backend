from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from ..models import UserProfile
from .serializer import UserProfileSerializer


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_profile(request, pk):
    """
    API endpoint to retrieve or update a UserProfile.

    GET:
        Returns the UserProfile of a user identified by user_id (pk).

    PATCH:
        Allows partial update of a user's UserProfile.
        Only authenticated users can perform this action.

    Args:
        request: HTTP request object.
        pk: Primary key of the user whose profile is to be retrieved or updated.

    Returns:
        HTTP response with UserProfile data or error status.
    """
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
@permission_classes([IsAuthenticated])
def business_profiles(request):
    """
    API endpoint to retrieve all business UserProfiles.

    Returns:
        List of all UserProfiles with user_type 'business'.
    """
    profiles = UserProfile.objects.filter(user_type=UserProfile.BUSINESS)
    serializer = UserProfileSerializer(profiles, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customer_profiles(request):
    """
    API endpoint to retrieve all customer UserProfiles.

    Returns:
        List of all UserProfiles with user_type 'customer'.
    """
    profiles = UserProfile.objects.filter(user_type=UserProfile.CUSTOMER)
    serializer = UserProfileSerializer(profiles, many=True)
    return Response(serializer.data)
