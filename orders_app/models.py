from django.db import models
from django.contrib.auth.models import User
from offers_app.models import OfferDetail 

class Order(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In_progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    business_user = models.ForeignKey(User, related_name='orders_received', on_delete=models.CASCADE)
    customer_user = models.ForeignKey(User, related_name='orders_placed', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    created_at = models.DateTimeField(auto_now_add=True)
    offer_detail = models.ForeignKey(OfferDetail, on_delete=models.CASCADE, related_name='orders', default="")
