from django.contrib.auth.models import User
from django.db import models

class Review(models.Model):
    """
    Modell für Bewertungen (Reviews) zwischen Benutzern.

    Attributes:
        business_user (ForeignKey): Der Nutzer, der bewertet wird (Empfänger der Bewertung).
        reviewer (ForeignKey): Der Nutzer, der die Bewertung schreibt.
        rating (IntegerField): Bewertungswert, typischerweise eine Sternebewertung.
        description (TextField): Freitextliche Beschreibung zur Bewertung.
        created_at (DateTimeField): Zeitpunkt der Erstellung der Bewertung (automatisch gesetzt).
        updated_at (DateTimeField): Zeitpunkt der letzten Aktualisierung (automatisch gesetzt).
    """
    business_user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='received_reviews',
        help_text='Der Nutzer, der die Bewertung erhält.'
    )
    reviewer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='written_reviews',
        help_text='Der Nutzer, der die Bewertung schreibt.'
    )
    rating = models.IntegerField(
        help_text='Bewertungswert als ganze Zahl (z.B. 1-5 Sterne).'
    )
    description = models.TextField(
        help_text='Freitextliche Beschreibung zur Bewertung.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        help_text='Zeitpunkt der Erstellung der Bewertung.'
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        help_text='Zeitpunkt der letzten Aktualisierung der Bewertung.'
    )

    def __str__(self):
        """
        Gibt eine aussagekräftige String-Repräsentation des Reviews zurück.
        Beispiel: "Review by alice for bob - 4 stars"
        """
        return f"Review by {self.reviewer.username} for {self.business_user.username} - {self.rating} stars"