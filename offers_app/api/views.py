from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Min, Max
from rest_framework import status, generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from user_app.models import UserProfile
from offers_app.api.filters import OfferFilter
from offers_app.models import Offer, OfferDetail
from .serializer import (
    OfferListSerializer,
    OfferCreateSerializer,
    OfferDetailSerializer,
    OfferPatchSerializer
)


class OfferDetailRetrieveView(generics.RetrieveAPIView):
    """
    GET /api/offer-details/<id>/
    Returns a single OfferDetail object by its ID.
    """
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    lookup_field = 'id'


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination class for paginating offers.
    """
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100



class OfferListView(generics.ListCreateAPIView):
    """
    GET /api/offers/ - Lists offers with pagination
    POST /api/offers/ - Creates a new offer without pagination
    """
    queryset = Offer.objects.all().prefetch_related('details', 'user').annotate(
        annotated_min_price=Min('details__price'),
        annotated_min_delivery_time=Min('details__delivery_time_in_days')
    )
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price', 'max_price']

    def get_queryset(self):
        return super().get_queryset().annotate(
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


    def paginate_queryset(self, queryset):
        if self.request.method == 'GET':
            paginator = StandardResultsSetPagination()
            return paginator.paginate_queryset(queryset, self.request, view=self)
        return None



class SingleOfferView(APIView):
    """
    Handles GET, PATCH, and DELETE for a single Offer instance.
    Permissions: Only the creator can PATCH or DELETE.
    """
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_object(self, id):
        try:
            return Offer.objects.get(pk=id)
        except Offer.DoesNotExist:
            return None

    def get(self, request, id):
        offer = self.get_object(id)
        if not offer:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = OfferListSerializer(offer)
        return Response(serializer.data)

    def patch(self, request, id):
        offer = self.get_object(id)
        if not offer:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        if offer.user != request.user:
            return Response({'detail': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = OfferPatchSerializer(offer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        offer = self.get_object(id)
        if not offer:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        if offer.user != request.user:
            return Response({'detail': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)
        offer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
