# gestion/models/inventory.py
from django.db import models
from .product import Product
from .zone import Zone

class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock', db_index=True)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='stock', db_index=True)
    quantity = models.PositiveIntegerField(default=0, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'zone') # Evita duplicados
        verbose_name_plural = "Inventories" # Corrige el plural en el admin
        indexes = [
            models.Index(fields=['product', 'quantity']),  # Índice compuesto para agregaciones
            models.Index(fields=['zone', 'quantity']),  # Índice para filtros por zona
        ]

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in {self.zone.name}"