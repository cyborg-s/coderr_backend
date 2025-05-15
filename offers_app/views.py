from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Offer
from .serializer import OfferSerializer

@api_view(['GET'])
def offer_details(request, id):
    try:
        offer = Offer.objects.get(pk=id)
    except Offer.DoesNotExist:
        return Response({'error': 'Offer not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = OfferSerializer(offer)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
def offers_list(request):
    if request.method == 'GET':
        offers = Offer.objects.all()
        serializer = OfferSerializer(offers, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = OfferSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PATCH', 'DELETE'])
def single_offer(request, id):
    try:
        offer = Offer.objects.get(pk=id)
    except Offer.DoesNotExist:
        return Response({'error': 'Offer not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = OfferSerializer(offer)
        return Response(serializer.data)
    
    elif request.method == 'PATCH':
        serializer = OfferSerializer(offer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        offer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
