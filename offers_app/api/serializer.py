from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import Offer, OfferDetail


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    """
    Serializes only the ID and a URL for the OfferDetail object
    to allow simple linking.
    """
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        return f"/offerdetails/{obj.id}/"


class UserDetailsSerializer(serializers.ModelSerializer):
    """
    Serializes basic user information displayed in offers.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']


class OfferListSerializer(serializers.ModelSerializer):
    """
    Serializes an offer including:
    - Links to related OfferDetails
    - Basic user information
    - Computed minimum values for price and delivery time
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
        Returns the annotated minimum price if available,
        otherwise uses the calculated value.
        """
        return getattr(obj, 'annotated_min_price', None) or obj.calculated_min_price

    def get_min_delivery_time(self, obj):
        """
        Returns the annotated minimum delivery time or the calculated value.
        """
        return getattr(obj, 'annotated_min_delivery_time', None) or obj.calculated_min_delivery_time


class OfferDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer for OfferDetail objects including all relevant fields.
    """
    class Meta:
        model = OfferDetail
        fields = [
            'id',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
        ]
        extra_kwargs = {
            'title': {'required': True},
            'revisions': {'required': True},
            'delivery_time_in_days': {'required': True},
            'price': {'required': True},
            'features': {'required': True},
            'offer_type': {'required': True},
        }


class OfferCreateSerializer(serializers.ModelSerializer):
    """
    Allows creating an offer with multiple nested OfferDetails in one request.
    """
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']

    def create(self, validated_data):
        """
        Overrides default create method to also create nested OfferDetails.
        """
        details_data = validated_data.pop('details')
        user = self.context['request'].user
        offer = Offer.objects.create(**validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer


class OfferPatchSerializer(serializers.ModelSerializer):
    """
    Supports updating an offer including nested OfferDetails.
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
        details_data = validated_data.pop('details', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if details_data:
            existing_details = {d.offer_type: d for d in instance.details.all()}

            for detail_data in details_data:
                offer_type = detail_data.get('offer_type')
                if not offer_type:
                    raise serializers.ValidationError("offer_type muss im Detail angegeben werden.")

                existing_detail = existing_details.get(offer_type)
                if not existing_detail:
                    raise serializers.ValidationError(f"Kein Detail mit offer_type '{offer_type}' gefunden.")

                detail_serializer = OfferDetailSerializer(existing_detail, data=detail_data, partial=True)
                detail_serializer.is_valid(raise_exception=True)
                detail_serializer.save()

        return instance
