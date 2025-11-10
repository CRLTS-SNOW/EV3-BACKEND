# gestion/models/sale_item.py
from django.db import models
from .sale import Sale
from .product import Product

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    
    # ¡Importante! Guardamos el precio al momento de la venta
    # por si el precio del producto cambia en el futuro.
    price_at_sale = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name if self.product else 'Producto Eliminado'}"

    @property
    def get_subtotal(self):
        """Calcula el subtotal del item (cantidad * precio)"""
        return self.quantity * self.price_at_sale