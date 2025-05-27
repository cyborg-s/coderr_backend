
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Avg

from reviews_app.models import Review
from user_app.models import UserProfile
from offers_app.models import Offer


class BaseInfoView(APIView):
    """
    API endpoint that provides general statistics about the platform.

    GET /api/baseinfo/

    Returns:
        - Total number of reviews
        - Average rating (rounded to 1 decimal place)
        - Number of business profiles
        - Total number of offers

    Permissions:
        - Publicly accessible (no authentication required).
    """
    permission_classes = [AllowAny]
    pagination_class = None

    def get(self, request):
        """
        Retrieve platform-wide statistics.

        Response example:
        {
            "review_count": 152,
            "average_rating": 4.3,
            "business_profile_count": 47,
            "offer_count": 89
        }

        Returns:
            200 OK with the statistics data.
        """
        review_count = Review.objects.count()
        average_rating = Review.objects.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        business_profile_count = UserProfile.objects.filter(user_type='business').count()
        offer_count = Offer.objects.count()

        data = {
            "review_count": review_count,
            "average_rating": round(average_rating, 1),
            "business_profile_count": business_profile_count,
            "offer_count": offer_count
        }

        return Response(data)
