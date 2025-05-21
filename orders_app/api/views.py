from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from ..models import Order
from .serializer import OrderSerializer
from user_app.models import UserProfile
from offers_app.models import OfferDetail


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def orders_list(request):
    """
    Listet alle Bestellungen des aktuell angemeldeten Nutzers auf (GET).
    Erlaubt es einem Kunden, eine neue Bestellung basierend auf einem OfferDetail zu erstellen (POST).
    
    GET:
        - Business-User sehen Bestellungen, bei denen sie als business_user eingetragen sind.
        - Kunden sehen ihre eigenen Bestellungen als customer_user.
    POST:
        - Erwartet 'offer_detail_id' im Request Body.
        - Erstellt eine neue Bestellung, die dem Angebot-Detail zugeordnet ist.
    """
    user = request.user
    
    if request.method == 'GET':
        # Business-User sehen ihre eingegangenen Bestellungen
        if getattr(user, 'profile', None) and user.profile.user_type == 'business':
            orders = Order.objects.filter(business_user=user)
        else:
            # Kunden sehen ihre eigenen Bestellungen
            orders = Order.objects.filter(customer_user=user)
        
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        offer_detail_id = request.data.get('offer_detail_id')
        if not offer_detail_id:
            return Response({'error': 'offer_detail_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            offer_detail = OfferDetail.objects.get(pk=offer_detail_id)
        except OfferDetail.DoesNotExist:
            return Response({'error': 'OfferDetail not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Bestellung erstellen mit Bezug auf das OfferDetail und den Nutzer als Kunden
        order = Order.objects.create(
            business_user=offer_detail.offer.user,
            customer_user=user,
            product_name=offer_detail.title,
            price=offer_detail.price,
            offer_detail=offer_detail
        )
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def order_details(request, id):
    """
    Detailansicht für eine einzelne Bestellung.
    - GET: Gibt die Bestelldetails zurück.
    - PATCH: Ermöglicht Business-Usern, eine Bestellung teilweise zu aktualisieren.
    - DELETE: Nur Staff-Mitglieder können eine Bestellung löschen.
    """
    order = get_object_or_404(Order, pk=id)
    
    if request.method == 'GET':
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    
    elif request.method == 'PATCH':
        # Prüfung, ob der Nutzer ein Business-User ist
        try:
            profile = UserProfile.objects.get(user_id=request.user.id)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_403_FORBIDDEN)
        
        if profile.user_type != 'business':
            return Response({'error': 'Only business users can update orders.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = OrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Nur Staff-Mitglieder dürfen Bestellungen löschen
        if not request.user.is_staff:
            return Response({'error': 'Only staff can delete orders.'}, status=status.HTTP_403_FORBIDDEN)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def order_count(request, buissness_user):
    """
    Liefert die Anzahl der Bestellungen für einen Business-User mit Status 'in_progress'.
    """
    count = Order.objects.filter(business_user=buissness_user, status='in_progress').count()
    return Response({'order_count': count})


@api_view(['GET'])
def completed_order_count(request, buissness_user):
    """
    Liefert die Anzahl der abgeschlossenen Bestellungen (Status 'completed') für einen Business-User.
    """
    count = Order.objects.filter(business_user=buissness_user, status='completed').count()
    return Response({'completed_order_count': count})