from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from .models import Review


class ReviewTests(APITestCase):
    """
    Test class for the review system.
    Covers creation, retrieval, update, and deletion of reviews.
    """

    def setUp(self):
        """
        Setup method called before each test.
        Creates two users (reviewer and business), logs in the reviewer,
        and creates a sample review.
        """
        self.reviewer = User.objects.create_user(username='reviewer', password='pass1234')
        self.business_user = User.objects.create_user(username='business', password='pass1234')
        self.client.login(username='reviewer', password='pass1234')
        self.review = Review.objects.create(
            reviewer=self.reviewer,
            business_user=self.business_user,
            rating=4,
            description='Good cooperation.'
        )

    def test_get_reviews_list(self):
        """
        Tests retrieving the full list of reviews.
        Expects at least one review in the response.
        """
        url = reverse('reviewslist')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_get_reviews_with_filters(self):
        """
        Tests filtering reviews by business_user_id.
        """
        url = reverse('reviewslist')
        response = self.client.get(url, {'business_user_id': self.business_user.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['business_user'], self.business_user.id)

    def test_create_review_success(self):
        """
        Tests successful creation of a review.
        """
        url = reverse('reviewslist')
        data = {
            'business_user': self.business_user.id,
            'rating': 5,
            'description': 'Excellent!'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['reviewer'], self.reviewer.id)
        self.assertEqual(response.data['business_user'], self.business_user.id)
        self.assertEqual(response.data['rating'], 5)

    def test_create_review_missing_fields(self):
        """
        Tests validation when creating a review with missing required fields.
        """
        url = reverse('reviewslist')
        data = {
            'business_user': self.business_user.id
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('rating', response.data)
        self.assertIn('description', response.data)

    def test_get_single_review(self):
        """
        Tests retrieving a single review.
        """
        url = reverse('reviewdetail', args=[self.review.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.review.id)

    def test_patch_review_by_owner(self):
        """
        Tests editing a review by its creator.
        """
        url = reverse('reviewdetail', args=[self.review.id])
        data = {
            'rating': 3,
            'description': 'Somewhat different than expected.'
        }

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 3)

    def test_patch_review_by_other_user_denied(self):
        """
        Tests that another user cannot edit a review they do not own.
        """
        other_user = User.objects.create_user(username='hacker', password='pass1234')
        self.client.login(username='hacker', password='pass1234')

        url = reverse('reviewdetail', args=[self.review.id])
        data = {'rating': 1}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_review_by_owner(self):
        """
        Tests deleting a review by its owner.
        """
        url = reverse('reviewdetail', args=[self.review.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(id=self.review.id).exists())

    def test_delete_review_by_other_user_denied(self):
        """
        Tests that another user cannot delete a review they do not own.
        """
        other_user = User.objects.create_user(username='hacker', password='pass1234')
        self.client.login(username='hacker', password='pass1234')

        url = reverse('reviewdetail', args=[self.review.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
