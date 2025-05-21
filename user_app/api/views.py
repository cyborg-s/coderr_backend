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
    API-Endpunkt zum Abrufen oder Aktualisieren eines UserProfiles.

    GET:
        Gibt das UserProfile eines Nutzers anhand der user_id (pk) zurück.

    PATCH:
        Ermöglicht partielles Aktualisieren des UserProfiles eines Nutzers.
        Nur authentifizierte Nutzer können diese Aktion ausführen.

    Args:
        request: HTTP Request-Objekt.
        pk: Primärschlüssel des Users, dessen Profil abgerufen oder aktualisiert werden soll.

    Returns:
        HTTP Response mit UserProfile-Daten oder Fehlerstatus.
    """
    try:
        # Versuche, das UserProfile anhand der user_id zu holen oder 404, wenn nicht gefunden
        profile = get_object_or_404(UserProfile, user_id=pk)
    except Exception:
        return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        # Teilweise Aktualisierung (patch) des Profils mit den übergebenen Daten
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        # Falls Validierung fehlschlägt, Fehler zurückgeben
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def business_profiles(request):
    """
    API-Endpunkt zum Abrufen aller Business-UserProfile.

    Returns:
        Liste aller UserProfile mit user_type 'business'.
    """
    profiles = UserProfile.objects.filter(user_type=UserProfile.BUSINESS)
    serializer = UserProfileSerializer(profiles, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def customer_profiles(request):
    """
    API-Endpunkt zum Abrufen aller Customer-UserProfile.

    Returns:
        Liste aller UserProfile mit user_type 'customer'.
    """
    profiles = UserProfile.objects.filter(user_type=UserProfile.CUSTOMER)
    serializer = UserProfileSerializer(profiles, many=True)
    return Response(serializer.data)