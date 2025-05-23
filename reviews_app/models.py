from django.contrib.auth.models import User
from django.db import models

class Review(models.Model):
    """
    Model for reviews between users.

    Attributes:
        business_user (ForeignKey): The user who is being reviewed (recipient of the review).
        reviewer (ForeignKey): The user who writes the review.
        rating (IntegerField): The rating value, typically a star rating.
        description (TextField): Free-text description of the review.
        created_at (DateTimeField): Timestamp when the review was created (set automatically).
        updated_at (DateTimeField): Timestamp when the review was last updated (set automatically).
    """
    business_user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='received_reviews',
        help_text='The user who receives the review.'
    )
    reviewer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='written_reviews',
        help_text='The user who writes the review.'
    )
    rating = models.IntegerField(
        help_text='Rating value as an integer (e.g., 1-5 stars).'
    )
    description = models.TextField(
        help_text='Free-text description of the review.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        help_text='Timestamp of when the review was created.'
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        help_text='Timestamp of the last update to the review.'
    )

    def __str__(self):
        """
        Returns a meaningful string representation of the review.
        Example: "Review by alice for bob - 4 stars"
        """
        return f"Review by {self.reviewer.username} for {self.business_user.username} - {self.rating} stars"
