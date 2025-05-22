from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from user_app.models import UserProfile
from reviews_app.models import Review
from offers_app.models import Offer, OfferDetail
from django.contrib.auth.models import User

class BaseInfoAPITest(TestCase):
    """
    Testklasse für die API, die Basisinformationen (wie Anzahl der Reviews, durchschnittliche Bewertung,
    Anzahl der Business-Profile und Anzahl der Angebote) bereitstellt.
    """

    def setUp(self):
        """
        Einrichtung der Testdaten:
        - Erstellen von zwei Usern mit unterschiedlichen Profiltypen ('business' und 'private')
        - Anlegen von zwei Angeboten, jeweils einem User zugeordnet
        - Erstellen von zugehörigen OfferDetails, um Mindestpreise und Lieferzeiten zu simulieren
        - Anlegen von Reviews zwischen den Usern zur Testung von Bewertungsstatistiken
        """
        self.client = APIClient()

        # Business-User und zugehöriges Profil anlegen
        user_business = User.objects.create(username='business_user')
        UserProfile.objects.create(user=user_business, user_type='business')

        # Privat-User und zugehöriges Profil anlegen
        user_private = User.objects.create(username='private_user')
        UserProfile.objects.create(user=user_private, user_type='private')

        # Zwei Angebote anlegen, je eines für business und private User
        offer1 = Offer.objects.create(
            user=user_business,
            title='Test Offer 1',
            description='Beschreibung 1',
        )
        offer2 = Offer.objects.create(
            user=user_private,
            title='Test Offer 2',
            description='Beschreibung 2',
        )

        # Angebotdetails hinzufügen, um min. Preis und Lieferzeit zu testen
        OfferDetail.objects.create(
            offer=offer1,
            title='Basic',
            revisions=1,
            delivery_time_in_days=3,
            price=100.00,
            features=['Feature A', 'Feature B'],
            offer_type='Basic'
        )
        OfferDetail.objects.create(
            offer=offer2,
            title='Premium',
            revisions=3,
            delivery_time_in_days=1,
            price=200.00,
            features=['Feature X', 'Feature Y'],
            offer_type='Premium'
        )

        # Reviews anlegen:
        # business_user wird von private_user bewertet (2 Bewertungen)
        Review.objects.create(
            business_user=user_business,
            reviewer=user_private,
            rating=4,
            description='Gute Arbeit'
        )
        Review.objects.create(
            business_user=user_business,
            reviewer=user_private,
            rating=5,
            description='Sehr zufrieden'
        )
        # private_user wird von business_user bewertet (1 Bewertung)
        Review.objects.create(
            business_user=user_private,
            reviewer=user_business,
            rating=3,
            description='Okay'
        )

    def test_baseinfo_status_code(self):
        """
        Testet, ob der Endpunkt '/api/base-info/' erfolgreich erreichbar ist (HTTP 200).
        """
        response = self.client.get('/api/base-info/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_baseinfo_response_content(self):
        """
        Testet den Antwortinhalt der Basis-Info-API:
        - Überprüfung, ob die erwarteten Felder enthalten sind
        - Überprüfung, ob die Werte korrekt berechnet wurden (Review-Anzahl, Durchschnittsbewertung,
          Anzahl Business-Profile, Anzahl Angebote)
        """
        response = self.client.get('/api/base-info/')
        data = response.json()

        # Erwartete Felder müssen vorhanden sein
        self.assertIn('review_count', data)
        self.assertIn('average_rating', data)
        self.assertIn('business_profile_count', data)
        self.assertIn('offer_count', data)

        # Werte prüfen:
        # Insgesamt wurden 3 Reviews erstellt
        self.assertEqual(data['review_count'], 3)
        # Durchschnittliche Bewertung berechnet aus (4 + 5 + 3) / 3 = 4.0
        self.assertEqual(data['average_rating'], 4.0)
        # Nur ein Business-Profil vorhanden
        self.assertEqual(data['business_profile_count'], 1)
        # Zwei Angebote insgesamt
        self.assertEqual(data['offer_count'], 2)