from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User

from offers_app.models import Offer, OfferDetail
from orders_app.models import Order
from user_app.models import UserProfile


class OrderTests(APITestCase):
    """
    Testklasse für die Order-API-Endpunkte.
    Testet das Erstellen von Bestellungen, das Abrufen von Bestellungen
    sowie das Zählen von Bestellungen für Business-User.
    """

    def setUp(self):
        """
        Setzt die Testumgebung auf:
        - Ein Business-User mit UserProfile "business"
        - Ein Customer-User mit UserProfile "customer"
        - Ein Angebot (Offer) mit einem zugehörigen Angebotsdetail (OfferDetail)
        """
        # Business-User erstellen und mit UserProfile markieren
        self.business_user = User.objects.create_user(username='businessuser', password='pass1234')
        UserProfile.objects.create(user=self.business_user, user_type='business')

        # Customer-User erstellen und mit UserProfile markieren
        self.customer_user = User.objects.create_user(username='customer', password='pass1234')
        UserProfile.objects.create(user=self.customer_user, user_type='customer')

        # Angebot (Offer) durch Business-User erstellen
        self.offer = Offer.objects.create(
            title='Angebot A',
            description='Beschreibung A',
            user=self.business_user
        )

        # Detailangaben zum Angebot (OfferDetail) erstellen
        self.offer_detail = OfferDetail.objects.create(
            offer=self.offer,
            title='Standard',
            price=199.99,
            revisions=2,
            delivery_time_in_days=5,
            features=["Basic", "Zuverlässig"],
            offer_type="Standard"
        )

    def test_create_order_success(self):
        """
        Testet die erfolgreiche Erstellung einer Bestellung über POST:
        - Als Customer eingeloggt
        - sendet offer_detail_id
        - Erwartet HTTP 201 Created
        - Prüft, ob Bestellung korrekt gespeichert wurde
        """
        self.client.login(username='customer', password='pass1234')
        url = reverse('orderslist')
        payload = {
            'offer_detail_id': self.offer_detail.id
        }

        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

        # Prüfen, ob gespeicherte Bestellung die richtigen Attribute hat
        order = Order.objects.first()
        self.assertEqual(order.business_user, self.business_user)
        self.assertEqual(order.customer_user, self.customer_user)
        self.assertEqual(order.offer_detail, self.offer_detail)
        self.assertEqual(order.status, 'in_progress')  # Standardstatus

    def test_create_order_without_offer_detail_id(self):
        """
        Testet Erstellung einer Bestellung ohne offer_detail_id:
        - Erwartet HTTP 400 Bad Request
        - Fehlermeldung für 'offer_detail_id' vorhanden
        """
        self.client.login(username='customer', password='pass1234')
        url = reverse('orderslist')
        payload = {}

        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('offer_detail_id', response.data['error'])

    def test_create_order_with_invalid_offer_detail(self):
        """
        Testet Erstellung einer Bestellung mit einem nicht existierenden offer_detail_id:
        - Erwartet HTTP 404 Not Found
        """
        self.client.login(username='customer', password='pass1234')
        url = reverse('orderslist')
        payload = {
            'offer_detail_id': 9999  # ID existiert nicht
        }

        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_orders_as_business_user(self):
        """
        Testet Abruf der Bestellungen als Business-User über GET:
        - Erstellt vorher eine Bestellung
        - Erwartet HTTP 200 OK
        - Response enthält genau 1 Bestellung
        """
        # Bestellung anlegen
        Order.objects.create(
            business_user=self.business_user,
            customer_user=self.customer_user,
            product_name='Standard',
            price=199.99,
            offer_detail=self.offer_detail
        )
        self.client.login(username='businessuser', password='pass1234')
        url = reverse('orderslist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_orders_as_customer(self):
        """
        Testet Abruf der Bestellungen als Customer-User über GET:
        - Erstellt vorher eine Bestellung
        - Erwartet HTTP 200 OK
        - Response enthält genau 1 Bestellung
        """
        Order.objects.create(
            business_user=self.business_user,
            customer_user=self.customer_user,
            product_name='Standard',
            price=199.99,
            offer_detail=self.offer_detail
        )
        self.client.login(username='customer', password='pass1234')
        url = reverse('orderslist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_order_count(self):
        """
        Testet den Endpunkt zur Zählung aller laufenden Bestellungen eines Business-Users:
        - Erstellt eine Bestellung mit Status 'in_progress'
        - Ruft URL mit business_user als URL-Parameter auf
        - Erwartet HTTP 200 OK
        - Response enthält order_count = 1
        """
        Order.objects.create(
            business_user=self.business_user,
            customer_user=self.customer_user,
            product_name='Standard',
            price=199.99,
            offer_detail=self.offer_detail,
            status='in_progress'
        )
        # Hinweis: 'buissness_user' ist vermutlich ein Tippfehler, sollte 'business_user' sein
        url = reverse('ordercount', kwargs={'buissness_user': self.business_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_count'], 1)

    def test_completed_order_count(self):
        """
        Testet den Endpunkt zur Zählung aller abgeschlossenen Bestellungen eines Business-Users:
        - Erstellt eine Bestellung mit Status 'completed'
        - Ruft URL mit business_user als URL-Parameter auf
        - Erwartet HTTP 200 OK
        - Response enthält completed_order_count = 1
        """
        Order.objects.create(
            business_user=self.business_user,
            customer_user=self.customer_user,
            product_name='Standard',
            price=199.99,
            offer_detail=self.offer_detail,
            status='completed'
        )
        # Hinweis: 'buissness_user' ist vermutlich ein Tippfehler, sollte 'business_user' sein
        url = reverse('completedordercount', kwargs={'buissness_user': self.business_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['completed_order_count'], 1)
