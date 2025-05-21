from rest_framework import serializers
from .models import Offer, OfferDetail
from django.contrib.auth.models import User

class OfferDetailLinkSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        return f"/offerdetails/{obj.id}/"


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']


class OfferListSerializer(serializers.ModelSerializer):
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
        return obj.min_price

    def get_min_delivery_time(self, obj):
        return obj.min_delivery_time


class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']

class OfferCreateSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)
    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(**validated_data, user=self.context['request'].user)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer
    

class OfferPatchSerializer(serializers.ModelSerializer):
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
        return obj.min_price

    def get_min_delivery_time(self, obj):
        return obj.min_delivery_time

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)

    # Hauptdaten aktualisieren
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

    # Details aktualisieren anhand der Reihenfolge
        if details_data:
            existing_details = list(instance.details.all().order_by('id'))  # oder offer_type

            for incoming_data, existing_detail in zip(details_data, existing_details):
                for attr, value in incoming_data.items():
                    setattr(existing_detail, attr, value)
                existing_detail.save()

        return instance