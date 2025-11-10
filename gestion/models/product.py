# gestion/models/product.py
from django.db import models
from django.db.models import Sum
from .supplier import Supplier # Importacion relativa

class Product(models.Model):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(
        Supplier, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='products'
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def total_quantity(self):
        # Suma el stock de 'Inventory' (que definiremos luego)
        result = self.stock.aggregate(total=Sum('quantity'))
        return result['total'] or 0