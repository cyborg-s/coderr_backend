from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Min, Max
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied
from rest_framework import status
from django.shortcuts import get_object_or_404
from user_app.models import UserProfile
from offers_app.filters import OfferFilter
from .models import Offer, OfferDetail
from .serializer import OfferListSerializer, OfferCreateSerializer, OfferDetailSerializer, OfferPatchSerializer

# -------------------------------------------
# Funktionale View: Holt ein einzelnes OfferDetail per ID
# -------------------------------------------
@api_view(['GET'])
def offer_details(request, id):
    """
    Gibt ein einzelnes OfferDetail-Objekt anhand der ID zurück.
    """
    try:
        offer = OfferDetail.objects.get(pk=id)
    except OfferDetail.DoesNotExist:
        return Response({'error': 'Offer not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = OfferDetailSerializer(offer)
    return Response(serializer.data, status=status.HTTP_200_OK)

# -------------------------------------------
# Pagination-Klasse für die Angeboteliste
# -------------------------------------------
class StandardResultsSetPagination(PageNumberPagination):
    """
    Definiert die Standard-Paginierung für Listenansichten.
    """
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100

# -------------------------------------------
# Klassenbasierte View: Liste und Erstellen von Angeboten
# -------------------------------------------
class OfferListView(ListCreateAPIView):
    """
    GET: Gibt eine Liste von Angeboten zurück (gefiltert, sortiert, paginiert).
    POST: Erstellt ein neues Angebot (nur für Business-User erlaubt).
    """
    queryset = Offer.objects.all().prefetch_related('details', 'user').annotate(
        annotated_min_price=Min('details__price'),
        annotated_min_delivery_time=Min('details__delivery_time_in_days')
    )
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price', 'max_price']

    def get_queryset(self):
        """
        Fügt zusätzliche Annotationen für Mindest- und Höchstpreis hinzu.
        """
        queryset = super().get_queryset()
        return queryset.annotate(
            min_price=Min('details__price'),
            max_price=Max('details__price')
        )

    def get_serializer_class(self):
        """
        Wählt den passenden Serializer basierend auf der HTTP-Methode.
        """
        if self.request.method == 'POST':
            return OfferCreateSerializer
        return OfferListSerializer

    def perform_create(self, serializer):
        """
        Stellt sicher, dass nur Business-User Angebote erstellen können.
        """
        user = self.request.user
        try:
            user_profile = UserProfile.objects.get(user_id=user.id)
        except UserProfile.DoesNotExist:
            raise PermissionDenied('User profile not found.')
        
        if user_profile.user_type == 'customer':
            raise PermissionDenied('Only business users can create offers.')

        serializer.save(user=user)

# -------------------------------------------
# Funktionale View: Einzelnes Angebot abrufen, bearbeiten oder löschen
# -------------------------------------------
@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def single_offer(request, id):
    """
    GET: Einzelnes Angebot abrufen.
    PATCH: Angebot bearbeiten (nur vom Ersteller).
    DELETE: Angebot löschen (nur vom Ersteller).
    """
    offer = get_object_or_404(Offer, pk=id)

    if request.method == 'GET':
        serializer = OfferListSerializer(offer)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        if offer.user != request.user:
            return Response({'error': 'You do not have permission to edit this offer.'},
                            status=status.HTTP_403_FORBIDDEN)
        serializer = OfferPatchSerializer(offer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if offer.user != request.user:
            return Response({'error': 'You do not have permission to delete this offer.'},
                            status=status.HTTP_403_FORBIDDEN)
        offer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)