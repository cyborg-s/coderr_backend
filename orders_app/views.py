from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Order
from .serializer import OrderSerializer

@api_view(['GET'])
def orders_list(request):
    orders = Order.objects.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def order_details(request, id):
    try:
        order = Order.objects.get(pk=id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = OrderSerializer(order)
    return Response(serializer.data)

@api_view(['GET'])
def order_count(request, buissness_user_id):
    count = Order.objects.filter(business_user_id=buissness_user_id).count()
    return Response({'order_count': count})

@api_view(['GET'])
def completed_order_count(request, buissness_user_id):
    count = Order.objects.filter(business_user_id=buissness_user_id, status='completed').count()
    return Response({'completed_order_count': count})