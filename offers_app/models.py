from django.db import models
from django.contrib.auth.models import User

class Offer(models.Model):
    """
    Model for an offer created by a user.
    An offer can have multiple detail entries (OfferDetail).
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='offers',
        help_text="The user who created this offer."
    )
    title = models.CharField(
        max_length=255,
        help_text="Title of the offer."
    )
    image = models.ImageField(
        upload_to='offers/',
        null=True,
        blank=True,
        help_text="Optional image for the offer."
    )
    description = models.TextField(
        help_text="Detailed description of the offer."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the offer was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp of the last update of the offer."
    )

    @property
    def calculated_min_price(self):
        """
        Calculates the minimum price among all related OfferDetail objects.
        Returns 0 if no details exist.
        """
        return self.details.aggregate(models.Min('price'))['price__min'] or 0
    
    @property
    def calculated_min_delivery_time(self):
        """
        Calculates the minimum delivery time (in days) among all related OfferDetail objects.
        Returns 0 if no details exist.
        """
        return self.details.aggregate(models.Min('delivery_time_in_days'))['delivery_time_in_days__min'] or 0


class OfferDetail(models.Model):
    """
    Model for detailed information about an offer.
    Each detail describes a variant of the offer with specific price, delivery time, etc.
    """
    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name='details',
        help_text="The associated offer to which this detail belongs."
    )
    title = models.CharField(
        max_length=255,
        help_text="Title or name of the offer variant."
    )
    revisions = models.IntegerField(
        help_text="Number of allowed revisions."
    )
    delivery_time_in_days = models.PositiveIntegerField(
        help_text="Delivery time in days for this variant."
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price of the offer variant."
    )
    features = models.JSONField(
        default=list,
        help_text="List of special features or characteristics of the offer."
    )
    offer_type = models.CharField(
        max_length=20,
        help_text="Type of the offer (e.g., Basic, Premium, etc.)."
    )
