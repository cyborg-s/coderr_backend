from django.db import models
from django.contrib.auth.models import User

from offers_app.models import OfferDetail 

class Order(models.Model):
    # Status choices for the order, with three possible states
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),  # Order is currently being processed
        ('completed', 'Completed'),      # Order is completed
        ('cancelled', 'Cancelled'),      # Order is cancelled
    ]

    # Business user who receives the order (provider)
    business_user = models.ForeignKey(
        User, 
        related_name='orders_received', 
        on_delete=models.CASCADE
    )
    
    # Customer user who places the order
    customer_user = models.ForeignKey(
        User, 
        related_name='orders_placed', 
        on_delete=models.CASCADE
    )
    
    # Name of the ordered product, usually derived from the OfferDetail
    product_name = models.CharField(max_length=255)
    
    # Price of the order
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Current status of the order
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='in_progress'
    )
    
    # Timestamp when the order was created
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Link to the associated OfferDetail, e.g., the product variant
    offer_detail = models.ForeignKey(
        OfferDetail, 
        on_delete=models.CASCADE, 
        related_name='orders'
    )

    def __str__(self):
        return f"Order {self.id} - {self.product_name} ({self.status})"
