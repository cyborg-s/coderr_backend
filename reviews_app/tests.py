from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from .models import Review


class ReviewTests(APITestCase):
    """
    Testklasse für das Review-System.
    Deckt Erstellung, Abruf, Aktualisierung und Löschung von Bewertungen ab.
    """

    def setUp(self):
        """
        Setup-Methode wird vor jedem Test aufgerufen.
        Erstellt zwei Benutzer (Reviewer und Business), loggt den Reviewer ein
        und legt ein Beispielreview an.
        """
        # Reviewer = Verfasser der Bewertung
        self.reviewer = User.objects.create_user(username='reviewer', password='pass1234')

        # Business = Bewerteter Benutzer
        self.business_user = User.objects.create_user(username='business', password='pass1234')

        # Reviewer einloggen (Session-Login, da kein Token verwendet wird)
        self.client.login(username='reviewer', password='pass1234')

        # Beispielhafte Bewertung für spätere Tests
        self.review = Review.objects.create(
            reviewer=self.reviewer,
            business_user=self.business_user,
            rating=4,
            description='Gute Zusammenarbeit.'
        )

    def test_get_reviews_list(self):
        """
        Testet das Abrufen der gesamten Review-Liste.
        Erwartet mindestens ein Review im Rückgabewert.
        """
        url = reverse('reviewslist')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_get_reviews_with_filters(self):
        """
        Testet das Filtern von Bewertungen nach business_user_id.
        """
        url = reverse('reviewslist')
        response = self.client.get(url, {'business_user_id': self.business_user.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['business_user'], self.business_user.id)

    def test_create_review_success(self):
        """
        Testet das erfolgreiche Erstellen einer Bewertung.
        """
        url = reverse('reviewslist')
        data = {
            'business_user': self.business_user.id,
            'rating': 5,
            'description': 'Hervorragend!'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['reviewer'], self.reviewer.id)
        self.assertEqual(response.data['business_user'], self.business_user.id)
        self.assertEqual(response.data['rating'], 5)

    def test_create_review_missing_fields(self):
        """
        Testet die Validierung beim Erstellen einer Bewertung mit fehlenden Pflichtfeldern.
        """
        url = reverse('reviewslist')
        data = {
            'business_user': self.business_user.id  # rating & description fehlen
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('rating', response.data)
        self.assertIn('description', response.data)

    def test_get_single_review(self):
        """
        Testet das Abrufen einer einzelnen Bewertung.
        """
        url = reverse('reviewdetail', args=[self.review.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.review.id)

    def test_patch_review_by_owner(self):
        """
        Testet das Bearbeiten einer Bewertung durch den Ersteller.
        """
        url = reverse('reviewdetail', args=[self.review.id])
        data = {
            'rating': 3,
            'description': 'Etwas anders als erwartet.'
        }

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 3)

    def test_patch_review_by_other_user_denied(self):
        """
        Testet, ob ein anderer User eine fremde Bewertung nicht bearbeiten darf.
        """
        # Anderen User einloggen
        other_user = User.objects.create_user(username='hacker', password='pass1234')
        self.client.login(username='hacker', password='pass1234')

        url = reverse('reviewdetail', args=[self.review.id])
        data = {'rating': 1}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_review_by_owner(self):
        """
        Testet das Löschen einer Bewertung durch den Besitzer.
        """
        url = reverse('reviewdetail', args=[self.review.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(id=self.review.id).exists())

    def test_delete_review_by_other_user_denied(self):
        """
        Testet, ob ein fremder User eine Bewertung nicht löschen darf.
        """
        other_user = User.objects.create_user(username='hacker', password='pass1234')
        self.client.login(username='hacker', password='pass1234')

        url = reverse('reviewdetail', args=[self.review.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
