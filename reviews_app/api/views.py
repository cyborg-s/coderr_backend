from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from ..models import Review
from .serializer import ReviewSerializer


class ReviewListCreateView(ListCreateAPIView):
    """
    GET:
        - Optional filtering by business_user_id and/or reviewer_id.
        - Optional ordering by rating or updated_at.
    POST:
        - Creates a new review with the logged-in user as reviewer.
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Review.objects.all()
        business_user_id = self.request.GET.get('business_user_id')
        reviewer_id = self.request.GET.get('reviewer_id')
        ordering = self.request.GET.get('ordering')

        if business_user_id:
            queryset = queryset.filter(business_user_id=business_user_id)
        if reviewer_id:
            queryset = queryset.filter(reviewer_id=reviewer_id)

        allowed_ordering = ['rating', '-rating', 'updated_at', '-updated_at']
        if ordering in allowed_ordering:
            queryset = queryset.order_by(ordering)

        return queryset

    def create(self, request, *args, **kwargs):
        if hasattr(request.user, 'profile') and request.user.profile.user_type == 'business':
            return Response(
                {'detail': 'Business users are not allowed to create reviews.'},
                status=status.HTTP_403_FORBIDDEN
            )

        data = request.data.copy()
        data['reviewer'] = request.user.id
        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReviewDetailView(RetrieveUpdateDestroyAPIView):
    """
    GET: Holt die Details einer Review.
    PATCH: Nur der Reviewer darf aktualisieren.
    DELETE: Nur der Reviewer darf löschen.
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(Review, pk=self.kwargs['id'])

    def patch(self, request, *args, **kwargs):
        review = self.get_object()
        if review.reviewer != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        review = self.get_object()
        if review.reviewer != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)
