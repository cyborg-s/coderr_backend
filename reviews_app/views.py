from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Review
from .serializer import ReviewSerializer

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def reviews_list(request):
    if request.method == 'GET':
        reviews = Review.objects.all()
        business_user_id = request.GET.get('business_user_id')
        reviewer_id = request.GET.get('reviewer_id')
        ordering = request.GET.get('ordering')
        if business_user_id:
            reviews = reviews.filter(business_user_id=business_user_id)
        if reviewer_id:
            reviews = reviews.filter(reviewer_id=reviewer_id)
        allowed_ordering_fields = ['rating', '-rating', 'updated_at', '-updated_at']
        if ordering in allowed_ordering_fields:
            reviews = reviews.order_by(ordering)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        data = request.data.copy()
        data['reviewer'] = request.user.id  # Reviewer automatisch setzen
        serializer = ReviewSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def review_detail(request, id):
    try:
        review = Review.objects.get(pk=id)
    except Review.DoesNotExist:
        return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ReviewSerializer(review)
        return Response(serializer.data)
    if review.reviewer != request.user:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'PATCH':
        serializer = ReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)