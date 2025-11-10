# gestion/models/inventory.py
from django.db import models
from .product import Product
from .zone import Zone

class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock')
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='stock')
    quantity = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'zone') # Evita duplicados
        verbose_name_plural = "Inventories" # Corrige el plural en el admin

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in {self.zone.name}"