from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from user_app.models import UserProfile

class AuthAPITestCase(APITestCase):
    """
    Testklasse für die Authentifizierungs-API:
    - Registrierung neuer Nutzer
    - Login bestehender Nutzer
    Es werden sowohl positive Fälle (erfolgreiche Registrierung/Login) als auch
    negative Fälle (ungültige Daten, falsches Passwort, nicht existierender Nutzer) getestet.
    """

    def setUp(self):
        """
        Vorbereitung der Testumgebung:
        - Ein existierender Nutzer mit Profil wird angelegt
        - URLs für Registrierung und Login werden als Strings definiert, da die Pfade über includes laufen
        """
        self.test_user = User.objects.create_user(
            username="existinguser",
            email="exist@example.com",
            password="strongpassword"
        )
        UserProfile.objects.create(user=self.test_user, user_type="Freelancer")

        # Pfade direkt als Strings, weil URLs in includes sind und reverse ggf. nicht funktioniert
        self.registration_url = '/api/registration/'
        self.login_url = '/api/login/'

    def test_registration_success(self):
        """
        Test für eine erfolgreiche Registrierung:
        - POST an /api/registration/ mit validen Daten
        - Erwartet wird HTTP 201 Created
        - Antwort enthält einen Auth-Token
        - Überprüfung, dass Benutzer und Profil korrekt angelegt wurden
        """
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123",
            "first_name": "New",
            "last_name": "User",
            "phone_number": "123456789",
            "address": "Teststraße 1",
            "type": "Kunde"
        }
        response = self.client.post(self.registration_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['username'], data['username'])
        self.assertEqual(response.data['email'], data['email'])

        # Validierung, ob User und UserProfile korrekt gespeichert wurden
        user = User.objects.get(username=data['username'])
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.user_type, data['type'])

    def test_registration_invalid_data(self):
        """
        Test für fehlerhafte Registrierung:
        - POST mit ungültigen Daten (leerer Username, fehlerhafte Email, kein Passwort)
        - Erwartet wird HTTP 400 Bad Request
        """
        data = {
            "username": "",
            "email": "invalidemail",
            "password": "",
            "type": "Kunde"
        }
        response = self.client.post(self.registration_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        """
        Test für erfolgreichen Login:
        - POST an /api/login/ mit korrektem Nutzernamen und Passwort
        - Erwartet wird HTTP 200 OK
        - Antwort enthält Token und korrekte Userdaten
        """
        data = {
            "username": self.test_user.username,
            "password": "strongpassword"
        }
        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['username'], self.test_user.username)
        self.assertEqual(response.data['email'], self.test_user.email)

    def test_login_invalid_password(self):
        """
        Test für Login mit falschem Passwort:
        - POST an /api/login/ mit korrektem Nutzernamen, aber falschem Passwort
        - Erwartet wird HTTP 400 Bad Request (Fehlerhafte Authentifizierung)
        """
        data = {
            "username": self.test_user.username,
            "password": "wrongpassword"
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_nonexistent_user(self):
        """
        Test für Login mit nicht vorhandenem Nutzer:
        - POST an /api/login/ mit Username, der nicht existiert
        - Erwartet wird HTTP 400 Bad Request
        """
        data = {
            "username": "noone",
            "password": "irrelevant"
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)