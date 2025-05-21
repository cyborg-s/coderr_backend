from django.http import JsonResponse
from django.db.models import Avg
from reviews_app.models import Review
from user_app.models import UserProfile
from offers_app.models import Offer

def baseinfo(request):
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
    return JsonResponse(data)