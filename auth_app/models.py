from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """
    Erweiterung des Django-Benutzermodells um zusätzliche Profilinformationen.

    Attribute:
        user (OneToOneField): Verbindung zum Django User.
        first_name (str): Vorname des Nutzers (optional).
        last_name (str): Nachname des Nutzers (optional).
        user_type (str): Art des Nutzers (z. B. "Freelancer", "Kunde").
        phone_number (str): Telefonnummer (optional).
        address (str): Adresse (optional).
        file (ImageField): Profilbild (optional).
        location (str): Standortangabe (optional).
        tel (str): Alternative Telefonnummer (optional).
        description (str): Beschreibung oder Biografie (optional).
        working_hours (str): Arbeitszeiten oder Verfügbarkeit (optional).
        created_at (datetime): Erstellungszeitpunkt des Profils (automatisch gesetzt).
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    user_type = models.CharField(max_length=20)
    # phone_number = models.CharField(max_length=20, blank=True)
    # address = models.CharField(max_length=255, blank=True)
    file = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    tel = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    working_hours = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Rückgabe des Benutzernamens zur Anzeige im Admin oder bei Debug-Ausgaben.
        """
        return f"{self.user.username}'s profile"