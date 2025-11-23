# gestion/models/product_movement.py
from django.db import models
from django.contrib.auth.models import User
from .product import Product
from .zone import Zone
from .warehouse import Warehouse
from .supplier import Supplier

class ProductMovement(models.Model):
    """
    Modelo de Movimiento de Productos según especificación
    Gestiona: ingresos, salidas, ajustes, devoluciones, transferencias
    """
    
    # Tipos de movimiento según especificación
    MOVEMENT_TYPES = [
        ('ingreso', 'Ingreso'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste'),
        ('devolucion', 'Devolución'),
        ('transferencia', 'Transferencia'),
    ]

    # --- 1. Datos del movimiento (según especificación) ---
    fecha = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha y hora del movimiento"
    )
    tipo = models.CharField(
        max_length=20,
        choices=MOVEMENT_TYPES,
        default='ingreso',
        help_text="Tipo de movimiento"
    )
    cantidad = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=0,
        help_text="Cantidad del movimiento"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='movements',
        help_text="Producto"
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movements',
        help_text="Proveedor (para ingresos)"
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movements',
        help_text="Bodega"
    )
    
    # Zona de Origen (para transferencias)
    origin_zone = models.ForeignKey(
        Zone,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movements_from',
        help_text="Zona de origen (para transferencias)"
    )
    
    # Zona de Destino
    destination_zone = models.ForeignKey(
        Zone,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movements_to',
        help_text="Zona de destino"
    )
    
    # --- 2. Control avanzado (según especificación) ---
    lote = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Número de lote (si aplica)"
    )
    serie = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Número de serie (si aplica)"
    )
    fecha_vencimiento = models.DateField(
        blank=True,
        null=True,
        help_text="Fecha de vencimiento (si aplica)"
    )
    
    # --- 3. Referencias/Observaciones (según especificación) ---
    doc_referencia = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Documento de referencia (OC-123, FAC-456, GUIA-789, etc.)"
    )
    motivo = models.TextField(
        blank=True,
        null=True,
        help_text="Motivo (para ajustes/devoluciones)"
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        help_text="Observaciones adicionales"
    )
    
    # Campos adicionales
    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movements_performed',
        help_text="Usuario que realizó el movimiento"
    )
    
    # Compatibilidad con campos antiguos
    movement_type = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Tipo de movimiento (compatibilidad)"
    )
    quantity = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Cantidad (compatibilidad)"
    )
    movement_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Fecha de movimiento (compatibilidad)"
    )
    reason = models.TextField(
        blank=True,
        null=True,
        help_text="Razón del movimiento (compatibilidad)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        tipo_display = self.get_tipo_display()
        return f"{tipo_display} - {self.product.name} ({self.cantidad})"
    
    def save(self, *args, **kwargs):
        # Mantener compatibilidad con campos antiguos
        if not self.movement_type:
            self.movement_type = self.tipo
        if not self.movement_date:
            self.movement_date = self.fecha
        if not self.quantity and self.cantidad:
            self.quantity = int(self.cantidad)
        if not self.reason:
            self.reason = self.motivo
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Movimiento de Producto"
        verbose_name_plural = "Movimientos de Productos"
        ordering = ['-fecha', '-created_at']
