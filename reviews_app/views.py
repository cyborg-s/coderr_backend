from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Review
from .serializer import ReviewSerializer

@api_view(['GET'])
def reviews_list(request):
    reviews = Review.objects.all()
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def review_detail(request, id):
    try:
        review = Review.objects.get(pk=id)
    except Review.DoesNotExist:
        return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = ReviewSerializer(review)
    return Response(serializer.data)