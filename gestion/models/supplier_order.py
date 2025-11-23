# gestion/models/supplier_order.py

from django.db import models
from django.contrib.auth.models import User
from .supplier import Supplier
from .warehouse import Warehouse
from .zone import Zone

class SupplierOrder(models.Model):
    """
    Orden de compra/pedido a un proveedor.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('RECEIVED', 'Recibida'),
        ('CANCELLED', 'Cancelada'),
    ]

    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='orders')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='orders', 
                                   help_text="Bodega destino del abastecimiento")
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='orders',
                            help_text="Zona específica donde se almacenará")
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                     related_name='supplier_orders',
                                     help_text="Usuario que realizó la solicitud")
    order_date = models.DateTimeField(auto_now_add=True)
    received_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True, null=True, help_text="Notas adicionales")
    
    class Meta:
        ordering = ['-order_date']
        verbose_name = "Orden a Proveedor"
        verbose_name_plural = "Órdenes a Proveedores"

    def __str__(self):
        supplier_name = self.supplier.razon_social or self.supplier.nombre_fantasia or 'N/A'
        return f"Orden #{self.id} - {supplier_name} - {self.get_status_display()}"
    
    @property
    def total_items(self):
        """Total de items en la orden"""
        return self.items.count()
    
    @property
    def total_quantity(self):
        """Cantidad total de productos solicitados"""
        from django.db.models import Sum
        return self.items.aggregate(total=Sum('quantity'))['total'] or 0


class SupplierOrderItem(models.Model):
    """
    Items de una orden a proveedor.
    """
    order = models.ForeignKey(SupplierOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='supplier_order_items')
    quantity = models.PositiveIntegerField(help_text="Cantidad solicitada")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, 
                                     help_text="Precio unitario (se toma del producto)")
    
    class Meta:
        verbose_name = "Item de Orden"
        verbose_name_plural = "Items de Orden"

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    @property
    def subtotal(self):
        """Subtotal del item"""
        return self.quantity * self.unit_price

