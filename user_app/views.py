from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import UserProfile
from .serializer import UserProfileSerializer

@api_view(['GET'])
def user_profile(request, pk):
    try:
        user = UserProfile.objects.get(pk=pk)
    except UserProfile.DoesNotExist:
        return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = UserProfileSerializer(user)
    return Response(serializer.data)

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