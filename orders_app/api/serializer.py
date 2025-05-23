from rest_framework import serializers

from ..models import Order

class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model. Includes additional read-only fields from the related OfferDetail 
    and associated Offer to provide a comprehensive representation of the order.
    """

    title = serializers.CharField(source='offer_detail.title', read_only=True)
    delivery_time_in_days = serializers.IntegerField(source='offer_detail.delivery_time_in_days', read_only=True)
    revisions = serializers.IntegerField(source='offer_detail.revisions', read_only=True)
    price = serializers.DecimalField(source='offer_detail.price', max_digits=10, decimal_places=2, read_only=True)
    features = serializers.JSONField(source='offer_detail.features', default=list, read_only=True)
    offer_type = serializers.CharField(source='offer_detail.offer_type', read_only=True)
    updated_at = serializers.DateTimeField(source='offer_detail.offer.updated_at', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'business_user',
            'customer_user',
            'status',
            'created_at',
            'updated_at',
            'product_name',
            'features',
            'offer_detail',
            'title',
            'delivery_time_in_days',
            'revisions',
            'price',
            'offer_type',
        ]
