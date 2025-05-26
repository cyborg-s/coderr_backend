from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """
    Extension of the Django User model to include additional profile data.
    Linked one-to-one with the User via OneToOneField.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    BUSINESS = 'business'
    CUSTOMER = 'customer'
    USER_TYPE_CHOICES = [
        (BUSINESS, 'Business'),
        (CUSTOMER, 'Customer'),
    ]

    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default=CUSTOMER)
    first_name = models.CharField(max_length=100, default="")
    last_name = models.CharField(max_length=100, default="")
    tel = models.CharField(max_length=15, blank=True,default="")  
    location = models.TextField(blank=True, default="")           
    description = models.TextField(blank=True, default="")         
    working_hours = models.TextField(blank=True, default="")      
    file = models.ImageField(upload_to='profiles/', blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.user_type})'
