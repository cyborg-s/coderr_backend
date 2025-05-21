from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Order
from .serializer import OrderSerializer
from user_app.models import UserProfile
from offers_app.models import OfferDetail
from django.shortcuts import get_object_or_404

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def orders_list(request):
    user = request.user
    if request.method == 'GET':
        if getattr(user, 'profile', None) and user.profile.user_type == 'business':
            orders = Order.objects.filter(business_user=user)
        else:
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
    order = get_object_or_404(Order, pk=id)
    if request.method == 'GET':
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    
    elif request.method == 'PATCH':
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
        if not request.user.is_staff:
            return Response({'error': 'Only staff can delete orders.'}, status=status.HTTP_403_FORBIDDEN)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def order_count(request, buissness_user):
    count = Order.objects.filter(business_user=buissness_user, status='in_progress').count()
    return Response({'order_count': count})


@api_view(['GET'])
def completed_order_count(request, buissness_user):
    count = Order.objects.filter(business_user=buissness_user, status='completed').count()
    return Response({'completed_order_count': count})