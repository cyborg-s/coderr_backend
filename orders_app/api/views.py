from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from django.shortcuts import get_object_or_404

from ..models import Order
from .serializer import OrderSerializer
from user_app.models import UserProfile
from offers_app.models import OfferDetail


class OrderListCreateView(ListCreateAPIView):
    """
    GET: Listet alle Bestellungen des aktuellen Nutzers auf.
    POST: Erstellt eine neue Bestellung für Kunden.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.profile.user_type == 'customer':
            return Order.objects.filter(customer_user=user)
        elif user.profile.user_type == 'business':
            return Order.objects.filter(offer_detail__offer__user=user)
        return Order.objects.none()

    def create(self, request, *args, **kwargs):
        user = request.user
        profile = getattr(user, 'profile', None)

        if not (profile and profile.user_type == 'customer'):
            return Response({'detail': 'Only customers can create orders.'}, status=status.HTTP_403_FORBIDDEN)

        offer_detail_id = request.data.get('offer_detail_id')
        if not offer_detail_id:
            return Response({'error': 'offer_detail_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            offer_detail = OfferDetail.objects.get(pk=offer_detail_id)
        except (OfferDetail.DoesNotExist, ValueError):
            return Response({'error': 'OfferDetail not found'}, status=status.HTTP_404_NOT_FOUND)

        order = Order.objects.create(
            business_user=offer_detail.offer.user,
            customer_user=user,
            product_name=offer_detail.title,
            price=offer_detail.price,
            offer_detail=offer_detail
        )

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class OrderDetailView(RetrieveUpdateDestroyAPIView):
    """
    GET: Holt Details zur Bestellung.
    PATCH: Nur Business-User dürfen aktualisieren.
    DELETE: Nur Staff darf löschen.
    """
    lookup_field = 'id'
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        try:
            profile = UserProfile.objects.get(user_id=request.user.id)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_403_FORBIDDEN)

        if profile.user_type != 'business':
            return Response({'error': 'Only business users can update orders.'}, status=status.HTTP_403_FORBIDDEN)

        return super().partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({'error': 'Only staff can delete orders.'}, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)



class OrderCountView(APIView):
    """
    Gibt die Anzahl der Bestellungen mit Status 'in_progress' für einen Business-User zurück.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user):
        try:
            UserProfile.objects.get(pk=business_user, user_type='business')
        except UserProfile.DoesNotExist:
            return Response({'detail': 'Business user not found.'}, status=status.HTTP_404_NOT_FOUND)

        count = Order.objects.filter(business_user=business_user, status='in_progress').count()
        return Response({'order_count': count}, status=status.HTTP_200_OK)


class CompletedOrderCountView(APIView):
    """
    Gibt die Anzahl der abgeschlossenen Bestellungen für einen Business-User zurück.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user):
        try:
            UserProfile.objects.get(pk=business_user, user_type='business')
        except UserProfile.DoesNotExist:
            return Response({'detail': 'Business user not found.'}, status=status.HTTP_404_NOT_FOUND)

        count = Order.objects.filter(business_user=business_user, status='completed').count()
        return Response({'completed_order_count': count}, status=status.HTTP_200_OK)
