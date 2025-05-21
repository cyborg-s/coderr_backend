from django.db import models
from django.contrib.auth.models import User

class Offer(models.Model):
    """
    Modell für ein Angebot, das von einem User erstellt wird.
    Ein Angebot kann mehrere Detail-Einträge (OfferDetail) haben.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='offers',
        help_text="Der Benutzer, der dieses Angebot erstellt hat."
    )
    title = models.CharField(
        max_length=255,
        help_text="Titel des Angebots."
    )
    image = models.ImageField(
        upload_to='offers/',
        null=True,
        blank=True,
        help_text="Optionales Bild zum Angebot."
    )
    description = models.TextField(
        help_text="Ausführliche Beschreibung des Angebots."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Zeitpunkt, zu dem das Angebot erstellt wurde."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Zeitpunkt der letzten Aktualisierung des Angebots."
    )

    @property
    def calculated_min_price(self):
        """
        Berechnet den minimalen Preis aller zugehörigen OfferDetail-Objekte.
        Falls keine Details vorhanden sind, wird 0 zurückgegeben.
        """
        return self.details.aggregate(models.Min('price'))['price__min'] or 0
    
    @property
    def calculated_min_delivery_time(self):
        """
        Berechnet die minimale Lieferzeit (in Tagen) aller zugehörigen OfferDetail-Objekte.
        Falls keine Details vorhanden sind, wird 0 zurückgegeben.
        """
        return self.details.aggregate(models.Min('delivery_time_in_days'))['delivery_time_in_days__min'] or 0


class OfferDetail(models.Model):
    """
    Modell für Detailinformationen zu einem Angebot.
    Jedes Detail beschreibt eine Variante des Angebots mit spezifischem Preis, Lieferzeit etc.
    """
    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name='details',
        help_text="Das zugehörige Angebot, zu dem dieses Detail gehört."
    )
    title = models.CharField(
        max_length=255,
        help_text="Titel oder Name der Angebotsvariante."
    )
    revisions = models.IntegerField(
        help_text="Anzahl der erlaubten Überarbeitungen/Revisionsrunden."
    )
    delivery_time_in_days = models.PositiveIntegerField(
        help_text="Lieferzeit in Tagen für diese Variante."
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Preis der Angebotsvariante."
    )
    features = models.JSONField(
        default=list,
        help_text="Liste der besonderen Merkmale oder Features des Angebots."
    )
    offer_type = models.CharField(
        max_length=20,
        help_text="Typ des Angebots (z.B. Basic, Premium, etc.)."
    )