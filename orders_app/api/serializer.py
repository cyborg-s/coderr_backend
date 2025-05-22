from rest_framework import serializers

from ..models import Order

class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer für das Order-Modell. Enthält zusätzliche ReadOnly-Felder aus dem verknüpften OfferDetail 
    und dem zugehörigen Offer, um eine umfassende Darstellung der Bestellung zu ermöglichen.
    """

    # Titel der Angebotsvariante (OfferDetail)
    title = serializers.CharField(source='offer_detail.title', read_only=True)

    # Lieferzeit in Tagen laut Angebot
    delivery_time_in_days = serializers.IntegerField(source='offer_detail.delivery_time_in_days', read_only=True)

    # Anzahl der Überarbeitungen, die im Angebot enthalten sind
    revisions = serializers.IntegerField(source='offer_detail.revisions', read_only=True)

    # Preis der gewählten Angebotsvariante
    price = serializers.DecimalField(source='offer_detail.price', max_digits=10, decimal_places=2, read_only=True)

    # Liste von Features/Funktionen der Angebotsvariante
    features = serializers.JSONField(source='offer_detail.features', default=list, read_only=True)

    # Typ des Angebots (z. B. Basic, Standard, Premium)
    offer_type = serializers.CharField(source='offer_detail.offer_type', read_only=True)

    # Zeitpunkt der letzten Aktualisierung des zugehörigen Offers
    updated_at = serializers.DateTimeField(source='offer.updated_at', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',                      # ID der Bestellung
            'business_user',           # Anbieter (Empfänger der Bestellung)
            'customer_user',           # Kunde (Auftraggeber)
            'status',                  # Aktueller Status der Bestellung
            'created_at',              # Zeitstempel der Bestellungserstellung
            'updated_at',              # Letzte Aktualisierung des zugehörigen Angebots
            'product_name',            # Produktname (vom OfferDetail abgeleitet)
            'features',                # Funktionsumfang laut Angebot
            'offer_detail',            # Referenz zur konkreten Angebotsvariante
            'title',                   # Titel der Angebotsvariante
            'delivery_time_in_days',   # Lieferzeit
            'revisions',               # Anzahl der Überarbeitungen
            'price',                   # Preis der Angebotsvariante
            'offer_type',              # Typ der Angebotsvariante
        ]
