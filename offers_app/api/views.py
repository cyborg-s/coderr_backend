from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Min, Max
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied
from rest_framework import status

from user_app.models import UserProfile
from offers_app.api.filters import OfferFilter
from ..models import Offer, OfferDetail
from .serializer import OfferListSerializer, OfferCreateSerializer, OfferDetailSerializer, OfferPatchSerializer


@api_view(['GET'])
def offer_details(request, id):
    """
    Returns a single OfferDetail object by ID.
    """
    try:
        offer = OfferDetail.objects.get(pk=id)
    except OfferDetail.DoesNotExist:
        return Response({'error': 'Offer not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = OfferDetailSerializer(offer)
    return Response(serializer.data, status=status.HTTP_200_OK)


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination for list views.
    """
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100


class OfferListView(ListCreateAPIView):
    """
    GET: Returns a list of offers (public).
    POST: Creates a new offer (only for authenticated business users).
    """
    queryset = Offer.objects.all().prefetch_related('details', 'user').annotate(
        annotated_min_price=Min('details__price'),
        annotated_min_delivery_time=Min('details__delivery_time_in_days')
    )
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price', 'max_price']

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.annotate(
            min_price=Min('details__price'),
            max_price=Max('details__price')
        ).order_by('id')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OfferCreateSerializer
        return OfferListSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]

    def perform_create(self, serializer):
        user = self.request.user
        try:
            user_profile = UserProfile.objects.get(user_id=user.id)
        except UserProfile.DoesNotExist:
            raise PermissionDenied('User profile not found.')

        if user_profile.user_type == 'customer':
            raise PermissionDenied('Only business users can create offers.')

        serializer.save(user=user)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def single_offer(request, id):
    """
    GET: Retrieve a single offer.
    PATCH: Update an offer (only by the creator).
    DELETE: Delete an offer (only by the creator).
    """
    try:
        offer = Offer.objects.get(pk=id)
    except Offer.DoesNotExist:
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method in ['PATCH', 'DELETE'] and offer.user != request.user:
        return Response({'detail': 'You do not have permission to perform this action.'},
                        status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = OfferListSerializer(offer)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        serializer = OfferPatchSerializer(offer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        offer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
