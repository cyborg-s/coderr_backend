from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from user_app.models import UserProfile
from rest_framework.authtoken.models import Token


class UserProfileAPITest(APITestCase):
    """
    Testklasse für alle API-Endpunkte, die mit UserProfile-Objekten zusammenhängen.
    Sie testet Authentifizierung, Datenabruf, -änderung und Fehlerfälle.
    """

    def setUp(self):
        """
        Erstellt zwei Testnutzer (Customer und Business) samt zugehöriger Profile
        und generiert Auth-Tokens für die spätere Authentifizierung in den Tests.
        """
        # Customer-Nutzer erstellen
        self.customer_user = User.objects.create_user(
            username='kunde', password='passwort123', email='kunde@example.com'
        )
        self.customer_profile = UserProfile.objects.create(
            user=self.customer_user,
            user_type='customer',
            first_name='Kunde',
            last_name='Test'
        )
        self.customer_token = Token.objects.create(user=self.customer_user)

        # Business-Nutzer erstellen
        self.business_user = User.objects.create_user(
            username='firma', password='passwort456', email='firma@example.com'
        )
        self.business_profile = UserProfile.objects.create(
            user=self.business_user,
            user_type='business',
            first_name='Firma',
            last_name='Test'
        )
        self.business_token = Token.objects.create(user=self.business_user)

    def authenticate(self, token):
        """
        Setzt den Authorization-Header für die API-Anfragen.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def test_get_customer_profile(self):
        """
        Testet, ob ein authentifizierter Kunde sein eigenes Profil abrufen kann.
        """
        self.authenticate(self.customer_token)
        url = reverse('userprofile', args=[self.customer_user.id])
        response = self.client.get(url)

        # Erwarteter HTTP-Status: 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Überprüfen, ob der Vorname korrekt zurückgegeben wird
        self.assertEqual(response.data['first_name'], 'Kunde')

    def test_patch_customer_profile_authenticated(self):
        """
        Testet, ob ein authentifizierter Kunde sein eigenes Profil bearbeiten kann.
        """
        self.authenticate(self.customer_token)
        url = reverse('userprofile', args=[self.customer_user.id])
        data = {'first_name': 'Geändert'}
        response = self.client.patch(url, data, format='json')

        # Erwarteter HTTP-Status: 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Überprüfen, ob die Änderung in der Datenbank gespeichert wurde
        self.customer_profile.refresh_from_db()
        self.assertEqual(self.customer_profile.first_name, 'Geändert')

    def test_patch_customer_profile_unauthenticated(self):
        """
        Testet, ob eine nicht authentifizierte PATCH-Anfrage abgewiesen wird.
        """
        url = reverse('userprofile', args=[self.customer_user.id])
        data = {'first_name': 'KeinZugang'}
        response = self.client.patch(url, data, format='json')

        # Erwarteter HTTP-Status: 401 Unauthorized (da kein Token übermittelt wurde)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_nonexistent_profile(self):
        """
        Testet den Fall, dass ein Nutzer versucht, ein nicht existierendes Profil abzurufen.
        """
        self.authenticate(self.customer_token)
        url = reverse('userprofile', args=[999])  # Nicht existierende ID
        response = self.client.get(url)

        # Erwarteter HTTP-Status: 404 Not Found
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_all_business_profiles(self):
        """
        Testet, ob alle Business-Profile abgerufen werden können.
        """
        url = reverse('businessprofiles')
        response = self.client.get(url)

        # Erwarteter HTTP-Status: 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Es sollte mindestens ein Business-Profil existieren
        self.assertGreaterEqual(len(response.data), 1)

        # Überprüfen, ob der Typ korrekt als "business" zurückgegeben wird
        self.assertEqual(response.data[0]['type'], 'business')

    def test_get_all_customer_profiles(self):
        """
        Testet, ob alle Customer-Profile abgerufen werden können.
        """
        url = reverse('customerprofiles')
        response = self.client.get(url)

        # Erwarteter HTTP-Status: 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Es sollte mindestens ein Customer-Profil existieren
        self.assertGreaterEqual(len(response.data), 1)

        # Überprüfen, ob der Typ korrekt als "customer" zurückgegeben wird
        self.assertEqual(response.data[0]['type'], 'customer')