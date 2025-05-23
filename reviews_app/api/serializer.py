from rest_framework import serializers

from ..models import Review

class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for the Review model.

    - Serializes all important fields of a review,
      including the business user being reviewed, the reviewer,
      the rating, description,
      as well as timestamps for creation and last update.
    """
    class Meta:
        model = Review
        fields = [
            'id',             
            'business_user',  
            'reviewer',       
            'rating',         
            'description',    
            'created_at',     
            'updated_at'      
        ]
