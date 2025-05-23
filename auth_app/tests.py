from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from user_app.models import UserProfile

class AuthAPITestCase(APITestCase):
    """
    Test class for the Authentication API:
    - Registration of new users
    - Login of existing users
    Both positive cases (successful registration/login) and
    negative cases (invalid data, wrong password, non-existing user) are tested.
    """

    def setUp(self):
        """
        Setup of the test environment:
        - Creates an existing user with profile
        - Defines URLs for registration and login as strings, since the paths are included via includes
        """
        self.test_user = User.objects.create_user(
            username="existinguser",
            email="exist@example.com",
            password="strongpassword"
        )
        UserProfile.objects.create(user=self.test_user, user_type="Freelancer")
        self.registration_url = '/api/registration/'
        self.login_url = '/api/login/'

    def test_registration_success(self):
        """
        Test for successful registration:
        - POST to /api/registration/ with valid data
        - Expects HTTP 201 Created
        - Response contains an auth token
        - Verifies that the user and profile were created correctly
        """
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123",
            "first_name": "New",
            "last_name": "User",
            "phone_number": "123456789",
            "address": "Test Street 1",
            "type": "Customer"
        }
        response = self.client.post(self.registration_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['username'], data['username'])
        self.assertEqual(response.data['email'], data['email'])

        user = User.objects.get(username=data['username'])
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.user_type, data['type'])

    def test_registration_invalid_data(self):
        """
        Test for faulty registration:
        - POST with invalid data (empty username, invalid email, no password)
        - Expects HTTP 400 Bad Request
        """
        data = {
            "username": "",
            "email": "invalidemail",
            "password": "",
            "type": "Customer"
        }
        response = self.client.post(self.registration_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        """
        Test for successful login:
        - POST to /api/login/ with correct username and password
        - Expects HTTP 200 OK
        - Response contains token and correct user data
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
        Test for login with wrong password:
        - POST to /api/login/ with correct username but wrong password
        - Expects HTTP 400 Bad Request (failed authentication)
        """
        data = {
            "username": self.test_user.username,
            "password": "wrongpassword"
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_nonexistent_user(self):
        """
        Test for login with non-existent user:
        - POST to /api/login/ with a username that does not exist
        - Expects HTTP 400 Bad Request
        """
        data = {
            "username": "noone",
            "password": "irrelevant"
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
