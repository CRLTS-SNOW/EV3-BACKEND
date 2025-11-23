# gestion/models/product_supplier.py
from django.db import models
from django.core.validators import MinValueValidator
from .product import Product
from .supplier import Supplier

class ProductSupplier(models.Model):
    """
    Relación entre Producto y Proveedor
    Permite múltiples proveedores por producto con diferentes costos y condiciones
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='supplier_relations',
        help_text="Producto"
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='product_relations',
        help_text="Proveedor"
    )
    
    # Campos según especificación
    costo = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        blank=False,
        null=False,
        validators=[MinValueValidator(0)],
        help_text="Costo del producto para este proveedor (requerido)"
    )
    lead_time_dias = models.IntegerField(
        default=7,
        blank=False,
        null=False,
        validators=[MinValueValidator(0)],
        help_text="Tiempo de entrega en días (requerido, default: 7)"
    )
    min_lote = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        default=1.0,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text="Cantidad mínima de compra"
    )
    descuento_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.0,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text="Porcentaje de descuento"
    )
    preferente = models.BooleanField(
        default=False,
        blank=False,
        null=False,
        help_text="Indica si es el proveedor preferente para este producto (requerido, default: False)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'supplier')
        verbose_name = "Relación Producto-Proveedor"
        verbose_name_plural = "Relaciones Producto-Proveedor"
        ordering = ['-preferente', 'costo']
    
    def clean(self):
        """Validar que solo un proveedor sea preferente por producto"""
        from django.core.exceptions import ValidationError
        
        if self.preferente:
            # Buscar otros proveedores preferentes para el mismo producto
            otros_preferentes = ProductSupplier.objects.filter(
                product=self.product,
                preferente=True
            )
            
            # Si estamos editando, excluir la instancia actual
            if self.pk:
                otros_preferentes = otros_preferentes.exclude(pk=self.pk)
            
            if otros_preferentes.exists():
                raise ValidationError({
                    'preferente': 'Ya existe un proveedor preferente para este producto. Solo puede haber uno por producto.'
                })
    
    def save(self, *args, **kwargs):
        """Validar antes de guardar"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        preferente_text = " (Preferente)" if self.preferente else ""
        return f"{self.product.name} - {self.supplier.razon_social}{preferente_text}"

