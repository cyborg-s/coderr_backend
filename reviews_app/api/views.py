from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from ..models import Review
from .serializer import ReviewSerializer

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def reviews_list(request):
    """
    Listet alle Reviews auf oder legt eine neue Review an.

    GET:
        - Optional Filter nach business_user_id und/oder reviewer_id.
        - Optional Sortierung nach rating oder updated_at (auf- oder absteigend).
        - Gibt die gefilterten und sortierten Reviews zurück.

    POST:
        - Erstellt eine neue Review.
        - Der angemeldete Benutzer wird automatisch als 'reviewer' gesetzt.
        - Validiert die eingehenden Daten und speichert die Review.
    """
    if request.method == 'GET':
        # Alle Reviews laden
        reviews = Review.objects.all()

        # Filterparameter aus Query-String auslesen
        business_user_id = request.GET.get('business_user_id')
        reviewer_id = request.GET.get('reviewer_id')
        ordering = request.GET.get('ordering')

        # Filter nach business_user falls angegeben
        if business_user_id:
            reviews = reviews.filter(business_user_id=business_user_id)

        # Filter nach reviewer falls angegeben
        if reviewer_id:
            reviews = reviews.filter(reviewer_id=reviewer_id)

        # Erlaubte Sortierfelder
        allowed_ordering_fields = ['rating', '-rating', 'updated_at', '-updated_at']

        # Nur erlaubte Sortierungen werden angewendet
        if ordering in allowed_ordering_fields:
            reviews = reviews.order_by(ordering)

        # Reviews serialisieren
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Daten kopieren, um den reviewer manuell zu setzen
        data = request.data.copy()
        data['reviewer'] = request.user.id  # Reviewer ist der aktuell angemeldete User

        # Serializer mit den Daten initialisieren
        serializer = ReviewSerializer(data=data)

        # Validierung prüfen
        if serializer.is_valid():
            serializer.save()
            # Erfolgreiche Erstellung - 201 Created
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # Fehlerhafte Eingaben - 400 Bad Request
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def review_detail(request, id):
    """
    Holt eine einzelne Review, aktualisiert sie oder löscht sie.

    GET:
        - Gibt die Review mit der angegebenen ID zurück.

    PATCH:
        - Aktualisiert die Review teilweise.
        - Nur der Ersteller (reviewer) darf die Review bearbeiten.

    DELETE:
        - Löscht die Review.
        - Nur der Ersteller (reviewer) darf löschen.
    """
    try:
        # Review mit der angegebenen ID laden
        review = Review.objects.get(pk=id)
    except Review.DoesNotExist:
        # Falls nicht gefunden, 404 zurückgeben
        return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # Review serialisieren und zurückgeben
        serializer = ReviewSerializer(review)
        return Response(serializer.data)

    # Berechtigung prüfen: Nur der Ersteller darf ändern oder löschen
    if review.reviewer != request.user:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'PATCH':
        # Teilweise Aktualisierung der Review
        serializer = ReviewSerializer(review, data=request.data, partial=True)

        # Validierung prüfen
        if serializer.is_valid():
            serializer.save()
            # Aktualisierte Daten zurückgeben
            return Response(serializer.data)

        # Validierungsfehler zurückgeben
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Review löschen
        review.delete()
        # Erfolgreiches Löschen mit 204 No Content bestätigen
        return Response(status=status.HTTP_204_NO_CONTENT)