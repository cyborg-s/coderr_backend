from rest_framework import serializers
from django.contrib.auth.models import User

from ..models import Offer, OfferDetail


# -------------------------------------------
# Serializer für die URL-Verlinkung von OfferDetail
# -------------------------------------------
class OfferDetailLinkSerializer(serializers.ModelSerializer):
    """
    Serialisiert nur die ID und eine URL zum OfferDetail-Objekt,
    um eine einfache Verlinkung zu ermöglichen.
    """
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        # Generiert die URL zum Detail-Endpunkt basierend auf der ID
        return f"/offerdetails/{obj.id}/"

# -------------------------------------------
# Serializer für grundlegende User-Daten
# -------------------------------------------
class UserDetailsSerializer(serializers.ModelSerializer):
    """
    Serialisiert die wichtigsten Nutzerdaten, die in Angeboten angezeigt werden.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']

# -------------------------------------------
# Serializer für Angebots-Listenansicht
# -------------------------------------------
class OfferListSerializer(serializers.ModelSerializer):
    """
    Serialisiert ein Angebot inklusive:
    - Verlinkung zu zugehörigen OfferDetails
    - Basis-Userinformationen
    - Berechnete Minimalwerte für Preis und Lieferzeit
    """
    details = OfferDetailLinkSerializer(many=True, read_only=True)
    user_details = UserDetailsSerializer(source='user', read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description',
            'created_at', 'updated_at', 'details',
            'min_price', 'min_delivery_time', 'user_details'
        ]

    def get_min_price(self, obj):
        """
        Gibt den annotierten Mindestpreis zurück, falls vorhanden,
        sonst wird ein berechneter Wert verwendet.
        """
        return getattr(obj, 'annotated_min_price', None) or obj.calculated_min_price

    def get_min_delivery_time(self, obj):
        """
        Gibt die annotierte minimale Lieferzeit zurück oder den berechneten Wert.
        """
        return getattr(obj, 'annotated_min_delivery_time', None) or obj.calculated_min_delivery_time

# -------------------------------------------
# Serializer für das OfferDetail-Model (vollständige Darstellung)
# -------------------------------------------
class OfferDetailSerializer(serializers.ModelSerializer):
    """
    Vollständiger Serializer für OfferDetail-Objekte mit allen wichtigen Feldern.
    """
    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']

# -------------------------------------------
# Serializer zum Erstellen eines Angebots inkl. verschachtelter OfferDetails
# -------------------------------------------
class OfferCreateSerializer(serializers.ModelSerializer):
    """
    Erlaubt das Erstellen eines Angebots mit mehreren OfferDetails in einem Request.
    """
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']

    def create(self, validated_data):
        """
        Überschreibt die Standard-Create-Methode, um
        die verschachtelten OfferDetails anzulegen.
        """
        details_data = validated_data.pop('details')
        # User wird aus Context (Request) bezogen, nicht aus Validated Data
        user = self.context['request'].user
        
        # Angebot mit dem authentifizierten User anlegen
        offer = Offer.objects.create(user=user, **validated_data)
        
        # Alle Details einzeln erstellen und dem Angebot zuordnen
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        
        return offer

# -------------------------------------------
# Serializer für partielle Aktualisierung (PATCH) von Angeboten inkl. Details
# -------------------------------------------
class OfferPatchSerializer(serializers.ModelSerializer):
    """
    Unterstützt die Aktualisierung eines Angebots mit verschachtelten OfferDetails.
    """
    details = OfferDetailSerializer(many=True)
    user_details = UserDetailsSerializer(source='user', read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description',
            'created_at', 'updated_at', 'details',
            'min_price', 'min_delivery_time', 'user_details'
        ]

    def get_min_price(self, obj):
        return obj.calculated_min_price

    def get_min_delivery_time(self, obj):
        return obj.calculated_min_delivery_time


    def update(self, instance, validated_data):
        """
        Überschreibt das Update, um auch verschachtelte OfferDetails zu aktualisieren.
        Vorhandene Details werden nacheinander mit den eingehenden Daten überschrieben.
        """
        details_data = validated_data.pop('details', None)

        # Normale Felder aktualisieren
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Wenn Details übergeben wurden, aktualisiere diese
        if details_data:
            existing_details = list(instance.details.all().order_by('id'))
            for incoming_data, existing_detail in zip(details_data, existing_details):
                for attr, value in incoming_data.items():
                    setattr(existing_detail, attr, value)
                existing_detail.save()
        return instance