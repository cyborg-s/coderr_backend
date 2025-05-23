from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

from offers_app.models import Offer, OfferDetail
from orders_app.models import Order
from user_app.models import UserProfile

User = get_user_model()

class OrderTests(APITestCase):
    """
    Test class for the Order API endpoints.
    Tests creating orders, retrieving orders,
    and counting orders for business users.
    """

    def setUp(self):
        """
        Sets up the test environment:
        - A business user with UserProfile "business"
        - A customer user with UserProfile "customer"
        - An offer (Offer) with a related offer detail (OfferDetail)
        """
        self.business_user = User.objects.create_user(username='businessuser', password='pass1234')
        UserProfile.objects.create(user=self.business_user, user_type='business')
        self.customer_user = User.objects.create_user(username='customer', password='pass1234')
        UserProfile.objects.create(user=self.customer_user, user_type='customer')
        self.offer = Offer.objects.create(
            title='Offer A',
            description='Description A',
            user=self.business_user
        )

        self.offer_detail = OfferDetail.objects.create(
            offer=self.offer,
            title='Standard',
            price=199.99,
            revisions=2,
            delivery_time_in_days=5,
            features=["Basic", "Reliable"],
            offer_type="Standard"
        )

    def test_create_order_success(self):
        """
        Tests successful creation of an order via POST:
        - Logged in as customer
        - Sends offer_detail_id
        - Expects HTTP 201 Created
        - Checks if the order was saved correctly
        """
        self.client.login(username='customer', password='pass1234')
        url = reverse('orderslist')
        payload = {
            'offer_detail_id': self.offer_detail.id
        }

        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.business_user, self.business_user)
        self.assertEqual(order.customer_user, self.customer_user)
        self.assertEqual(order.offer_detail, self.offer_detail)
        self.assertEqual(order.status, 'in_progress')

    def test_create_order_without_offer_detail_id(self):
        """
        Tests order creation without offer_detail_id:
        - Expects HTTP 400 Bad Request
        - Checks for error message regarding 'offer_detail_id'
        """
        self.client.login(username='customer', password='pass1234')
        url = reverse('orderslist')
        payload = {}

        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('offer_detail_id', response.data['error'])

    def test_create_order_with_invalid_offer_detail(self):
        """
        Tests order creation with a non-existent offer_detail_id:
        - Expects HTTP 404 Not Found
        """
        self.client.login(username='customer', password='pass1234')
        url = reverse('orderslist')
        payload = {
            'offer_detail_id': 9999
        }

        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_orders_as_business_user(self):
        """
        Tests retrieving orders as a business user via GET:
        - Creates an order beforehand
        - Expects HTTP 200 OK
        - Response contains exactly one order
        """
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
        Tests retrieving orders as a customer user via GET:
        - Creates an order beforehand
        - Expects HTTP 200 OK
        - Response contains exactly one order
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
        Tests the endpoint that counts all ongoing orders for a business user:
        """
        Order.objects.create(
            business_user=self.business_user,
            customer_user=self.customer_user,
            product_name='Standard',
            price=199.99,
            offer_detail=self.offer_detail,
            status='in_progress'
        )

        self.client.login(username='customer', password='pass1234')
        url = reverse('ordercount', kwargs={'buissness_user': self.business_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_count'], 1)

    def test_completed_order_count(self):
        """
        Tests the endpoint that counts all completed orders for a business user:
        """
        Order.objects.create(
            business_user=self.business_user,
            customer_user=self.customer_user,
            product_name='Standard',
            price=199.99,
            offer_detail=self.offer_detail,
            status='completed'
        )

        self.client.login(username='customer', password='pass1234')
        url = reverse('completedordercount', kwargs={'buissness_user': self.business_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['completed_order_count'], 1)

    def test_business_user_cannot_create_order(self):
        """
        Tests that a business user is forbidden from creating an order.
        Expects HTTP 403 Forbidden with appropriate error message.
        """
        self.client.force_authenticate(user=self.business_user)
        response = self.client.post('/api/orders/', {'offer_detail_id': self.offer_detail.id})
        self.assertEqual(response.status_code, 403)
        self.assertIn('Only customers are allowed', response.data['detail'])
