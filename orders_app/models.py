from django.db import models
from django.contrib.auth.models import User
from offers_app.models import OfferDetail 

class Order(models.Model):
    # Status-Auswahl für den Auftrag, mit drei möglichen Zuständen
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),  # Auftrag wird gerade bearbeitet
        ('completed', 'Completed'),      # Auftrag abgeschlossen
        ('cancelled', 'Cancelled'),      # Auftrag storniert
    ]

    # Geschäftlicher Nutzer, der die Bestellung erhält (Anbieter)
    business_user = models.ForeignKey(
        User, 
        related_name='orders_received', 
        on_delete=models.CASCADE
    )
    
    # Kunden-Nutzer, der die Bestellung aufgibt
    customer_user = models.ForeignKey(
        User, 
        related_name='orders_placed', 
        on_delete=models.CASCADE
    )
    
    # Name des bestellten Produkts, in der Regel vom OfferDetail abgeleitet
    product_name = models.CharField(max_length=255)
    
    # Preis der Bestellung
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Aktueller Status der Bestellung
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='in_progress'
    )
    
    # Zeitpunkt, an dem die Bestellung erstellt wurde
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Verknüpfung zum zugehörigen OfferDetail, z.B. die Produktvariante
    offer_detail = models.ForeignKey(
    OfferDetail, 
    on_delete=models.CASCADE, 
    related_name='orders'
)

    def __str__(self):
        return f"Order {self.id} - {self.product_name} ({self.status})"