from rest_framework import serializers

from ..models import Review

class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer für das Review-Modell.

    - serialisiert alle wichtigen Felder eines Reviews,
      darunter den bewerteten Business User, den Reviewer,
      die Bewertung (rating), Beschreibung (description)
      sowie Zeitstempel für Erstellung und Aktualisierung.
    """
    class Meta:
        model = Review
        fields = [
            'id',             # Primärschlüssel der Review
            'business_user',  # User, der bewertet wird (Empfänger der Bewertung)
            'reviewer',       # User, der die Bewertung abgegeben hat
            'rating',         # Bewertungswert (z.B. Sterne)
            'description',    # Freitextliche Beschreibung zur Bewertung
            'created_at',     # Zeitpunkt der Erstellung der Review
            'updated_at'      # Zeitpunkt der letzten Aktualisierung
        ]