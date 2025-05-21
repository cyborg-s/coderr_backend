from rest_framework.generics import ListCreateAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied
from rest_framework import status
from django.shortcuts import get_object_or_404
from user_app.models import UserProfile
from .models import Offer, OfferDetail
from .serializer import OfferListSerializer, OfferCreateSerializer, OfferDetailSerializer, OfferPatchSerializer

@api_view(['GET'])
def offer_details(request, id):
    try:
        offer = OfferDetail.objects.get(pk=id)
    except Offer.DoesNotExist:
        return Response({'error': 'Offer not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = OfferDetailSerializer(offer)
    return Response(serializer.data, status=status.HTTP_200_OK)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class OfferListView(ListCreateAPIView):
    queryset = Offer.objects.all().prefetch_related('details', 'user')
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OfferCreateSerializer
        return OfferListSerializer

    def perform_create(self, serializer):
        user = self.request.user

        try:
            user_profile = UserProfile.objects.get(user_id=user.id)
        except UserProfile.DoesNotExist:
            raise PermissionDenied('User profile not found.')

        if user_profile.user_type == 'customer':
            raise PermissionDenied('Only business users can create offers.')

        serializer.save()

@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def single_offer(request, id):
    offer = get_object_or_404(Offer, pk=id)

    if request.method == 'GET':
        serializer = OfferListSerializer(offer)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        if offer.user != request.user:
            return Response({'error': 'You do not have permission to edit this offer.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = OfferPatchSerializer(offer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if offer.user != request.user:
            return Response({'error': 'You do not have permission to delete this offer.'}, status=status.HTTP_403_FORBIDDEN)
        
        offer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)