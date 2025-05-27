from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from user_app.models import UserProfile
from offers_app.models import OfferDetail, Offer
from .models import Order

class OrderAPITestCase(APITestCase):

    def setUp(self):
        # Erstelle Business User
        self.business_user = User.objects.create_user(username='business', password='pass123')
        UserProfile.objects.create(user=self.business_user, user_type='business')

        # Erstelle Customer User
        self.customer_user = User.objects.create_user(username='customer', password='pass123')
        UserProfile.objects.create(user=self.customer_user, user_type='customer')

        # Erstelle Offer und OfferDetail
        self.offer = Offer.objects.create(user=self.business_user, title='Test Offer', description='Desc')
        self.offer_detail = OfferDetail.objects.create(
            offer=self.offer,
            title='Test Detail',
            revisions=2,
            delivery_time_in_days=5,
            price=99.99,
            features={"feature1": True},
            offer_type='standard'
        )

        # Erstelle eine Order
        self.order = Order.objects.create(
            business_user=self.business_user,
            customer_user=self.customer_user,
            product_name=self.offer_detail.title,
            price=self.offer_detail.price,
            offer_detail=self.offer_detail,
            status='in_progress'
        )

        self.client = APIClient()

    def test_order_list_as_customer(self):
        self.client.login(username='customer', password='pass123')
        url = reverse('orders:orderslist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Kunde soll seine eigenen Orders sehen
        self.assertTrue(any(order['id'] == self.order.id for order in response.data))

    def test_order_list_as_business(self):
        self.client.login(username='business', password='pass123')
        url = reverse('orders:orderslist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Business soll Orders für seine Offers sehen
        self.assertTrue(any(order['id'] == self.order.id for order in response.data))

    def test_create_order_as_customer(self):
        self.client.login(username='customer', password='pass123')
        url = reverse('orders:orderslist')
        data = {'offer_detail_id': self.offer_detail.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['product_name'], self.offer_detail.title)
        self.assertEqual(response.data['price'], str(self.offer_detail.price))

    def test_create_order_as_business_forbidden(self):
        self.client.login(username='business', password='pass123')
        url = reverse('orders:orderslist')
        data = {'offer_detail_id': self.offer_detail.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_order_detail_get(self):
        self.client.login(username='customer', password='pass123')
        url = reverse('orders:orderdetails', kwargs={'id': self.order.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.order.id)

    def test_order_update_patch_as_business(self):
        self.client.login(username='business', password='pass123')
        url = reverse('orders:orderdetails', kwargs={'id': self.order.id})
        data = {'status': 'completed'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'completed')

    def test_order_update_patch_as_customer_forbidden(self):
        self.client.login(username='customer', password='pass123')
        url = reverse('orders:orderdetails', kwargs={'id': self.order.id})
        data = {'status': 'completed'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_order_delete_as_staff(self):
        staff_user = User.objects.create_user(username='staff', password='pass123', is_staff=True)
        self.client.login(username='staff', password='pass123')
        url = reverse('orders:orderdetails', kwargs={'id': self.order.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=self.order.id).exists())

    def test_order_delete_as_non_staff_forbidden(self):
        self.client.login(username='business', password='pass123')
        url = reverse('orders:orderdetails', kwargs={'id': self.order.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_order_count_view(self):
        self.client.login(username='business', password='pass123')
        url = reverse('ordercount:ordercount', kwargs={'business_user': self.business_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_count'], 1)

    def test_completed_order_count_view(self):
        # Set order status to completed for test
        self.order.status = 'completed'
        self.order.save()
        self.client.login(username='business', password='pass123')
        url = reverse('completedordercount:completedordercount', kwargs={'business_user': self.business_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['completed_order_count'], 1)
