from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """
    Extension of the Django User model with additional profile information.

    Attributes:
        user (OneToOneField): Link to the Django User.
        first_name (str): User's first name (optional).
        last_name (str): User's last name (optional).
        user_type (str): Type of user (e.g., "Freelancer", "Customer").
        phone_number (str): Phone number (optional).
        address (str): Address (optional).
        file (ImageField): Profile picture (optional).
        location (str): Location information (optional).
        tel (str): Alternative phone number (optional).
        description (str): Description or biography (optional).
        working_hours (str): Working hours or availability (optional).
        created_at (datetime): Timestamp when the profile was created (auto-set).
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    user_type = models.CharField(max_length=20)
    file = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    tel = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    working_hours = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns the username for display in the admin or debug output.
        """
        return f"{self.user.username}'s profile"
