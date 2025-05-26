from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from user_app.models import UserProfile
from rest_framework.authtoken.models import Token


class UserProfileAPITest(APITestCase):
    """
    Test class for all API endpoints related to UserProfile objects.
    It tests authentication, data retrieval, modification, and error cases.
    """

    def setUp(self):
        """
        Creates two test users (Customer and Business) with associated profiles
        and generates auth tokens for authentication in the tests.
        """
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
        Sets the Authorization header for API requests.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def test_get_customer_profile(self):
        """
        Tests that an authenticated customer can retrieve their own profile.
        """
        self.authenticate(self.customer_token)
        url = reverse('userprofile:userprofile', args=[self.customer_user.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Kunde')

    def test_patch_customer_profile_authenticated(self):
        """
        Tests that an authenticated customer can modify their own profile.
        """
        self.authenticate(self.customer_token)
        url = reverse('userprofile:userprofile', args=[self.customer_user.id])
        data = {'first_name': 'Geändert'}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.customer_profile.refresh_from_db()
        self.assertEqual(self.customer_profile.first_name, 'Geändert')

    def test_patch_customer_profile_unauthenticated(self):
        """
        Tests that an unauthenticated PATCH request is rejected.
        """
        url = reverse('userprofile:userprofile', args=[self.customer_user.id])
        data = {'first_name': 'KeinZugang'}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_nonexistent_profile(self):
        """
        Tests the case when a user attempts to retrieve a non-existent profile.
        """
        self.authenticate(self.customer_token)
        url = reverse('userprofile:userprofile', args=[999])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_all_business_profiles(self):
        """
        Tests retrieving all business profiles.
        """
        self.authenticate(self.business_token)
        url = reverse('userprofiles:businessprofiles')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data['results'][0]['type'], 'business')

    def test_get_all_customer_profiles(self):
        """
        Tests retrieving all customer profiles.
        """
        self.authenticate(self.customer_token)
        url = reverse('userprofiles:customerprofiles')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data['results'][0]['type'], 'customer')
