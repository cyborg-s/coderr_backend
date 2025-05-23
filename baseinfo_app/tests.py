from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from user_app.models import UserProfile
from reviews_app.models import Review
from offers_app.models import Offer, OfferDetail
from django.contrib.auth.models import User

class BaseInfoAPITest(TestCase):
    """
    Test class for the API that provides basic information
    (such as the number of reviews, average rating,
    number of business profiles, and number of offers).
    """

    def setUp(self):
        """
        Setup test data:
        - Create two users with different profile types ('business' and 'private')
        - Create two offers, each assigned to one user
        - Create related OfferDetails to simulate minimum prices and delivery times
        - Create reviews between users to test rating statistics
        """
        self.client = APIClient()
        user_business = User.objects.create(username='business_user')
        UserProfile.objects.create(user=user_business, user_type='business')
        user_private = User.objects.create(username='private_user')
        UserProfile.objects.create(user=user_private, user_type='private')

        offer1 = Offer.objects.create(
            user=user_business,
            title='Test Offer 1',
            description='Description 1',
        )
        offer2 = Offer.objects.create(
            user=user_private,
            title='Test Offer 2',
            description='Description 2',
        )

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
        Review.objects.create(
            business_user=user_business,
            reviewer=user_private,
            rating=4,
            description='Good work'
        )
        Review.objects.create(
            business_user=user_business,
            reviewer=user_private,
            rating=5,
            description='Very satisfied'
        )

        Review.objects.create(
            business_user=user_private,
            reviewer=user_business,
            rating=3,
            description='Okay'
        )

    def test_baseinfo_status_code(self):
        """
        Tests whether the endpoint '/api/base-info/' is accessible successfully (HTTP 200).
        """
        response = self.client.get('/api/base-info/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_baseinfo_response_content(self):
        """
        Tests the response content of the base info API:
        - Verifies that the expected fields are included
        - Verifies that the values are calculated correctly (review count, average rating,
          number of business profiles, number of offers)
        """
        response = self.client.get('/api/base-info/')
        data = response.json()
        self.assertIn('review_count', data)
        self.assertIn('average_rating', data)
        self.assertIn('business_profile_count', data)
        self.assertIn('offer_count', data)
        self.assertEqual(data['review_count'], 3)
        self.assertEqual(data['average_rating'], 4.0)
        self.assertEqual(data['business_profile_count'], 1)
        self.assertEqual(data['offer_count'], 2)
