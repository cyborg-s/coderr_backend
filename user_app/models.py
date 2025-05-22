from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """
    Erweiterung des Django-User-Modells um zusätzliche Profildaten.
    Verknüpft sich 1:1 mit dem User über OneToOneField.
    """

    # 1:1-Beziehung zu User, mit rückwärtsgerichtetem Zugriff via 'profile'
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # Definierte Benutzer-Typen
    BUSINESS = 'business'
    CUSTOMER = 'customer'

    USER_TYPE_CHOICES = [
        (BUSINESS, 'Business'),
        (CUSTOMER, 'Customer'),
    ]

    # Art des Nutzers (Business oder Customer), Default ist 'customer'
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default=CUSTOMER)

    # Persönliche Daten
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    # Kontaktinformationen (optional)
    tel = models.CharField(max_length=15, blank=True, null=True)  # Telefonnummer
    location = models.TextField(blank=True, default="")           # ausführliche Ortsbeschreibung

    # Weitere Profilinfos
    description = models.TextField(blank=True, null=True)         # Beschreibung des Users
    working_hours = models.TextField(blank=True, null=True)       # Arbeitszeiten als Freitext

    # Profilbild (optional)
    file = models.ImageField(upload_to='profiles/', null=True, blank=True)

    # Zeitpunkt der Profilerstellung (automatisch gesetzt)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Repräsentation des Profils in Admin und Debug
        return f'{self.first_name} {self.last_name} ({self.user_type})'