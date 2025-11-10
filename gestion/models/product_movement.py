# gestion/models/product_movement.py
from django.db import models
from django.contrib.auth.models import User
from .product import Product
from .zone import Zone

class ProductMovement(models.Model):
    
    # Opciones claras para el tipo de movimiento
    MOVEMENT_TYPES = [
        ('ENTRY', 'Entrada de Stock'), # Ingreso de stock nuevo
        ('EXIT', 'Salida de Stock'),  # Venta o merma
        ('TRANSFER', 'Transferencia Interna'), # Mover entre zonas
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='movements')
    
    # La cantidad SIEMPRE es positiva
    quantity = models.PositiveIntegerField() 
    
    movement_type = models.CharField(
        max_length=20, 
        choices=MOVEMENT_TYPES
    )
    
    # Zona de Origen (Nulo si es 'ENTRY')
    origin_zone = models.ForeignKey(
        Zone, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='movements_from'
    )
    
    # Zona de Destino (Nulo si es 'EXIT')
    destination_zone = models.ForeignKey(
        Zone, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='movements_to'
    )
    
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    movement_date = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True, null=True) # Motivo (ej. "Venta Cliente", "Ajuste")

    def __str__(self):
        # Muestra el nombre legible, ej: "Entrada de Stock"
        return f"{self.get_movement_type_display()} of {self.product.name}"