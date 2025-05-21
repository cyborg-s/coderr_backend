

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
    Registrierung eines neuen Benutzers.

    Erstellt einen neuen User, ein zugehöriges UserProfile und gibt ein Auth-Token zurück.

    Body-Parameter:
    - username (str)
    - email (str)
    - password (str)
    - first_name (str)
    - last_name (str)
    - phone_number (str)
    - address (str)
    - type (str): Benutzerrolle oder -typ

    Antwort (201 Created):
    - token (str): Auth-Token
    - username (str)
    - email (str)
    - user_id (int)
    """
    # Extrahiere die notwendigen User-Daten aus der Anfrage
    user_data = {
        "username": request.data.get("username"),
        "email": request.data.get("email"),
        "password": request.data.get("password")
    }

    # Serialisiere und überprüfe die Benutzerdaten
    user_serializer = UserSerializer(data=user_data)
    if user_serializer.is_valid():
        # Benutzer speichern
        user = user_serializer.save()

        # Authentifizierungs-Token generieren oder abrufen
        token, created = Token.objects.get_or_create(user=user)

        # Benutzerprofil mit weiteren Feldern erstellen
        profile = UserProfile.objects.create(
            user=user,
            first_name=request.data.get('first_name', ''),
            last_name=request.data.get('last_name', ''),
            user_type=request.data.get('type'),
            phone_number=request.data.get('phone_number', ''),
            address=request.data.get('address', ''),
        )

        # Rückgabe der Authentifizierungsdaten
        return Response({
            'token': token.key,
            'username': user.username,
            'email': user.email,
            'user_id': user.id
        }, status=status.HTTP_201_CREATED)

    # Rückgabe von Fehlern bei ungültigen Daten
    return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Benutzer-Login.

    Erwartet gültige Zugangsdaten (Benutzername und Passwort) und gibt bei Erfolg Authentifizierungsdaten zurück.

    Body-Parameter:
    - username (str)
    - password (str)

    Antwort (200 OK):
    - token (str)
    - user_id (int)
    - username (str)
    """
    serializer = LoginSerializer(data=request.data)

    # Prüfen, ob die eingegebenen Login-Daten korrekt sind
    if serializer.is_valid():
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    # Rückgabe von Fehlern bei ungültigen Login-Daten
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
