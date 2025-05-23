from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User

from offers_app.models import Offer, OfferDetail
from user_app.models import UserProfile

class OfferApiTests(APITestCase):
    """
    Test class for the API endpoints related to Offers and OfferDetails.

    Various scenarios are tested, including:
    - Retrieving lists of offers
    - Creating, updating, and deleting offers (allowed only for business users)
    - Access control (no editing/deleting for customers)
    - Retrieving single offer and offer details
    """

    def setUp(self):
        """
        Prepare test data:
        - Create a business user and a customer user with corresponding UserProfiles
        - Create a sample offer with two offer details (Basic and Premium)
        """
        # Create business user
        self.business_user = User.objects.create_user(username='businessuser', password='pass1234')
        UserProfile.objects.create(user=self.business_user, user_type='business')

        # Create customer user
        self.customer_user = User.objects.create_user(username='customeruser', password='pass1234')
        UserProfile.objects.create(user=self.customer_user, user_type='customer')

        # Create sample offer
        self.offer = Offer.objects.create(
            user=self.business_user,
            title='Test Offer',
            description='Description Test',
        )
        # Create offer details (different price tiers/features)
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
        Tests retrieving the list of offers by an authenticated user.
        Expects status 200 and at least one offer in the results.
        Also checks if the title, minimum price, and minimum delivery time are correct.
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
        Tests creating a new offer by a business user.
        The offer includes multiple offer details.
        Expects status 201 CREATED and correct saving of offer and details.
        """
        self.client.login(username='businessuser', password='pass1234')
        url = reverse('offerslist')
        payload = {
            "title": "New Offer",
            "description": "New description",
            "details": [
                {
                    "title": "Standard",
                    "revisions": 3,
                    "delivery_time_in_days": 7,
                    "price": 150.00,
                    "features": ["Fast", "Reliable"],
                    "offer_type": "Standard"
                },
                {
                    "title": "Express",
                    "revisions": 1,
                    "delivery_time_in_days": 2,
                    "price": 250.00,
                    "features": ["Very fast"],
                    "offer_type": "Express"
                },
                {
                    "title": "Test",
                    "revisions": 1,
                    "delivery_time_in_days": 2,
                    "price": 250.00,
                    "features": ["Very fast"],
                    "offer_type": "Express"
                }
            ]
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Offer.objects.filter(title="New Offer").count(), 1)
        created_offer = Offer.objects.get(title="New Offer")
        self.assertEqual(created_offer.details.count(), 3)
        self.assertEqual(created_offer.user, self.business_user)

    def test_create_offer_as_customer_denied(self):
        """
        Tests that customers (user_type='customer') are not allowed to create an offer.
        Expects status 403 FORBIDDEN.
        """
        self.client.login(username='customeruser', password='pass1234')
        url = reverse('offerslist')
        payload = {
            "title": "Not Allowed",
            "description": "Customer not allowed",
            "details": []
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_single_offer(self):
        """
        Tests retrieving a single offer by ID.
        Expects status 200 OK and correct offer data returned.
        """
        self.client.login(username='businessuser', password='pass1234')
        url = reverse('singleoffer', kwargs={'id': self.offer.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.offer.id)

    def test_patch_offer_by_owner(self):
        """
        Tests updating an offer and its details by the owner (business user).
        Expects status 200 OK and correct modification of fields.
        """
        self.client.login(username='businessuser', password='pass1234')
        url = reverse('singleoffer', kwargs={'id': self.offer.id})
        payload = {
            "title": "Changed Title",
            "details": [
                {
                    "title": "Basic updated",
                    "revisions": 3,
                    "delivery_time_in_days": 4,
                    "price": 120.00,
                    "features": ["Updated Feature"],
                    "offer_type": "Basic"
                },
                {
                    "title": "Premium updated",
                    "revisions": 6,
                    "delivery_time_in_days": 1,
                    "price": 220.00,
                    "features": ["Updated Feature 2"],
                    "offer_type": "Premium"
                }
            ]
        }
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.offer.refresh_from_db()
        self.assertEqual(self.offer.title, "Changed Title")

        # Check if offer details were updated
        details = list(self.offer.details.order_by('id'))
        self.assertEqual(details[0].title, "Basic updated")
        self.assertEqual(details[0].price, 120.00)

    def test_patch_offer_not_owner_forbidden(self):
        """
        Tests that a non-owner user (e.g. customer) cannot update an offer.
        Expects status 403 FORBIDDEN.
        """
        self.client.login(username='customeruser', password='pass1234')
        url = reverse('singleoffer', kwargs={'id': self.offer.id})
        payload = {"title": "Attempted Change"}
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_offer_by_owner(self):
        """
        Tests deleting an offer by the owner (business user).
        Expects status 204 NO CONTENT and that the offer no longer exists.
        """
        self.client.login(username='businessuser', password='pass1234')
        url = reverse('singleoffer', kwargs={'id': self.offer.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Offer.objects.filter(id=self.offer.id).exists())

    def test_delete_offer_not_owner_forbidden(self):
        """
        Tests that a non-owner user (customer) cannot delete an offer.
        Expects status 403 FORBIDDEN.
        """
        self.client.login(username='customeruser', password='pass1234')
        url = reverse('singleoffer', kwargs={'id': self.offer.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_offer_detail(self):
        """
        Tests retrieving a single offer detail by ID.
        Expects status 200 OK and correct detail data returned.
        """
        self.client.login(username='businessuser', password='pass1234')
        url = reverse('offerdetails', kwargs={'id': self.detail1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.detail1.id)
        self.assertEqual(response.data['title'], self.detail1.title)

    def test_get_offer_detail_not_found(self):
        """
        Tests retrieving a non-existing offer detail.
        Expects status 404 NOT FOUND.
        """
        self.client.login(username='businessuser', password='pass1234')
        url = reverse('offerdetails', kwargs={'id': 999999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)