from rest_framework.generics import RetrieveUpdateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from ..models import UserProfile
from .serializer import UserProfileSerializer


class UserProfileView(RetrieveUpdateAPIView):
    """
    GET: Retrieve a user's profile by user_id.
    PATCH: Authenticated users can update their own profile only.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_object(self):
        profile = get_object_or_404(UserProfile, user_id=self.kwargs['pk'])

        if self.request.method == 'PATCH' and self.request.user.id != profile.user.id:
            self.permission_denied(
                self.request,
                message='You are not allowed to update this profile.'
            )
        return profile


class BusinessProfilesView(ListAPIView):
    """
    GET: List all business user profiles.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return UserProfile.objects.filter(user_type=UserProfile.BUSINESS)


class CustomerProfilesView(ListAPIView):
    """
    GET: List all customer user profiles.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return UserProfile.objects.filter(user_type=UserProfile.CUSTOMER)
