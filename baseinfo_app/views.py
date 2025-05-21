from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Avg
from reviews_app.models import Review
from user_app.models import UserProfile
from offers_app.models import Offer


@api_view(['GET'])
@permission_classes([AllowAny])
def baseinfo(request):
    """
    GET /api/baseinfo/

    Gibt allgemeine Statistikdaten zur Plattform zurück.

    Response:
        {
            "review_count": int,              # Anzahl aller Bewertungen
            "average_rating": float,          # Durchschnittliche Bewertung (gerundet auf eine Nachkommastelle)
            "business_profile_count": int,    # Anzahl der Business-Profile
            "offer_count": int                # Anzahl aller Angebote
        }
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
