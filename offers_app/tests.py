from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User

from offers_app.models import Offer, OfferDetail
from user_app.models import UserProfile

class OfferApiTests(APITestCase):
    """
    Testklasse für die API-Endpunkte rund um Angebote (Offers) und Angebotsdetails (OfferDetails).

    Es werden verschiedene Szenarien getestet, darunter:
    - Listen von Angeboten abrufen
    - Angebote anlegen, ändern und löschen (nur für business Nutzer erlaubt)
    - Zugriffskontrollen (keine Bearbeitung/Löschung für Kunden)
    - Einzelnes Angebot und Angebotsdetails abrufen
    """

    def setUp(self):
        """
        Vorbereitung der Testdaten:
        - Erstellen eines Business-Users und eines Customer-Users mit entsprechenden UserProfiles
        - Erstellen eines Beispielangebots mit zwei Angebotsdetails (Basic und Premium)
        """
        # Business-User anlegen
        self.business_user = User.objects.create_user(username='businessuser', password='pass1234')
        UserProfile.objects.create(user=self.business_user, user_type='business')

        # Kunden-User anlegen
        self.customer_user = User.objects.create_user(username='customeruser', password='pass1234')
        UserProfile.objects.create(user=self.customer_user, user_type='customer')

        # Beispiel-Angebot anlegen
        self.offer = Offer.objects.create(
            user=self.business_user,
            title='Test Offer',
            description='Beschreibung Test',
        )
        # Angebotsdetails anlegen (verschiedene Preisklassen/Features)
        self.detail1 = OfferDetail.objects.create(
            offer=self.offer,
            title='Basic',
            revisions=2,
            delivery_time_in_days=5,
            price=100.00,
            features=['Feature1', 'Feature2'],
            offer_type='Basic'
        )
        self.detail2 = OfferDetail.objects.create(
            offer=self.offer,
            title='Premium',
            revisions=5,
            delivery_time_in_days=2,
            price=200.00,
            features=['FeatureA', 'FeatureB'],
            offer_type='Premium'
        )

    def test_list_offers_authenticated(self):
        """
        Testet das Abrufen der Angebotsliste durch einen authentifizierten User.
        Erwartet Status 200 und mindestens ein Angebot in den Ergebnissen.
        Außerdem wird geprüft, ob der Titel, der minimale Preis und minimale Lieferzeit korrekt sind.
        """
        self.client.login(username='businessuser', password='pass1234')
        url = reverse('offerslist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertGreaterEqual(len(response.data['results']), 1)
        offer_data = response.data['results'][0]
        self.assertEqual(offer_data['title'], self.offer.title)
        self.assertEqual(offer_data['min_price'], 100.00)
        self.assertEqual(offer_data['min_delivery_time'], 2)

    def test_create_offer_as_business_user(self):
        """
        Testet das Erstellen eines neuen Angebots durch einen Business-User.
        Das Angebot enthält mehrere Angebotsdetails.
        Erwartet Status 201 CREATED und korrekte Speicherung von Angebot und Details.
        """
        self.client.login(username='businessuser', password='pass1234')
        url = reverse('offerslist')
        payload = {
            "title": "Neues Angebot",
            "description": "Beschreibung neu",
            "details": [
                {
                    "title": "Standard",
                    "revisions": 3,
                    "delivery_time_in_days": 7,
                    "price": "150.00",
                    "features": ["Schnell", "Zuverlässig"],
                    "offer_type": "Standard"
                },
                {
                    "title": "Express",
                    "revisions": 1,
                    "delivery_time_in_days": 2,
                    "price": "250.00",
                    "features": ["Sehr schnell"],
                    "offer_type": "Express"
                },
                {
                    "title": "Test",
                    "revisions": 1,
                    "delivery_time_in_days": 2,
                    "price": "250.00",
                    "features": ["Sehr schnell"],
                    "offer_type": "Express"
                }
            ]
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Offer.objects.filter(title="Neues Angebot").count(), 1)
        created_offer = Offer.objects.get(title="Neues Angebot")
        self.assertEqual(created_offer.details.count(), 3)
        self.assertEqual(created_offer.user, self.business_user)

    def test_create_offer_as_customer_denied(self):
        """
        Testet, dass Kunden (user_type='customer') kein Angebot erstellen dürfen.
        Erwartet Status 403 FORBIDDEN.
        """
        self.client.login(username='customeruser', password='pass1234')
        url = reverse('offerslist')
        payload = {
            "title": "Nicht erlaubt",
            "description": "Kunde darf nicht",
            "details": []
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_single_offer(self):
        """
        Testet das Abrufen eines einzelnen Angebots nach ID.
        Erwartet Status 200 OK und Rückgabe des korrekten Angebots.
        """
        self.client.login(username='businessuser', password='pass1234')
        url = reverse('singleoffer', kwargs={'id': self.offer.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.offer.id)

    def test_patch_offer_by_owner(self):
        """
        Testet das Aktualisieren eines Angebots und seiner Details durch den Besitzer (business user).
        Erwartet Status 200 OK und korrekte Änderung der Felder.
        """
        self.client.login(username='businessuser', password='pass1234')
        url = reverse('singleoffer', kwargs={'id': self.offer.id})
        payload = {
            "title": "Geänderter Titel",
            "details": [
                {
                    "title": "Basic updated",
                    "revisions": 3,
                    "delivery_time_in_days": 4,
                    "price": "120.00",
                    "features": ["Updated Feature"],
                    "offer_type": "Basic"
                },
                {
                    "title": "Premium updated",
                    "revisions": 6,
                    "delivery_time_in_days": 1,
                    "price": "220.00",
                    "features": ["Updated Feature 2"],
                    "offer_type": "Premium"
                }
            ]
        }
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.offer.refresh_from_db()
        self.assertEqual(self.offer.title, "Geänderter Titel")

        # Prüfen, ob Angebotsdetails aktualisiert wurden
        details = list(self.offer.details.order_by('id'))
        self.assertEqual(details[0].title, "Basic updated")
        self.assertEqual(details[0].price, 120.00)

    def test_patch_offer_not_owner_forbidden(self):
        """
        Testet, dass ein nicht-eigentlicher Nutzer (z.B. Kunde) ein Angebot nicht ändern darf.
        Erwartet Status 403 FORBIDDEN.
        """
        self.client.login(username='customeruser', password='pass1234')
        url = reverse('singleoffer', kwargs={'id': self.offer.id})
        payload = {"title": "Versuch Änderung"}
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_offer_by_owner(self):
        """
        Testet das Löschen eines Angebots durch den Besitzer (business user).
        Erwartet Status 204 NO CONTENT und dass das Angebot nicht mehr existiert.
        """
        self.client.login(username='businessuser', password='pass1234')
        url = reverse('singleoffer', kwargs={'id': self.offer.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Offer.objects.filter(id=self.offer.id).exists())

    def test_delete_offer_not_owner_forbidden(self):
        """
        Testet, dass ein nicht-eigentlicher Nutzer (Kunde) ein Angebot nicht löschen darf.
        Erwartet Status 403 FORBIDDEN.
        """
        self.client.login(username='customeruser', password='pass1234')
        url = reverse('singleoffer', kwargs={'id': self.offer.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_offer_detail(self):
        """
        Testet das Abrufen eines einzelnen Angebotsdetails nach ID.
        Erwartet Status 200 OK und Rückgabe des korrekten Details.
        """
        self.client.login(username='businessuser', password='pass1234')
        url = reverse('offerdetails', kwargs={'id': self.detail1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.detail1.id)
        self.assertEqual(response.data['title'], self.detail1.title)

    def test_get_offer_detail_not_found(self):
        """
        Testet den Abruf eines nicht vorhandenen Angebotsdetails.
        Erwartet Status 404 NOT FOUND.
        """
        self.client.login(username='businessuser', password='pass1234')
        url = reverse('offerdetails', kwargs={'id': 999999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)