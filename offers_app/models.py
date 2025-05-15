from django.db import models

class Offer(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class OfferDetail(models.Model):
    offer = models.OneToOneField(Offer, on_delete=models.CASCADE, related_name='details')
    availability = models.CharField(max_length=100, blank=True)
    shipping_info = models.TextField(blank=True)
    warranty_period_months = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Details for {self.offer.title}"