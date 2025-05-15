from django.db import models

class UserProfile(models.Model):
    BUSINESS = 'business'
    CUSTOMER = 'customer'
    
    USER_TYPE_CHOICES = [
        (BUSINESS, 'Business'),
        (CUSTOMER, 'Customer'),
    ]
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default=CUSTOMER)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    # profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.user_type})'