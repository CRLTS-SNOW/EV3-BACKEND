# gestion/models/product.py
from django.db import models
from django.db.models import Sum, Q
from django.core.validators import MinValueValidator

class Product(models.Model):
    """
    Modelo de Producto según especificación del proyecto Lili's
    """
    
    # --- 1. Identificación (según especificación) ---
    sku = models.CharField(
        max_length=50, 
        unique=True,
        help_text="SKU único del producto"
    )
    ean_upc = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        help_text="Código EAN/UPC (opcional, único si se usa)"
    )
    name = models.CharField(
        max_length=200,
        blank=False,
        null=False,
        db_index=True,  # Índice para optimizar búsquedas por nombre
        help_text="Nombre del producto (requerido)"
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text="Descripción detallada del producto (opcional)"
    )
    categoria = models.CharField(
        max_length=100,
        default='General',
        blank=False,
        null=False,
        db_index=True,  # Índice para optimizar filtros por categoría
        help_text="Categoría del producto (requerido)"
    )
    marca = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Marca del producto"
    )
    modelo = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Modelo del producto"
    )
    
    # --- 2. Unidades y precios (según especificación) ---
    uom_compra = models.CharField(
        max_length=20,
        default='UN',
        blank=False,
        null=False,
        help_text="Unidad de medida de compra (requerido, ej: UN, CAJA, KG)"
    )
    uom_venta = models.CharField(
        max_length=20,
        default='UN',
        blank=False,
        null=False,
        help_text="Unidad de medida de venta (requerido)"
    )
    factor_conversion = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=1.0,
        blank=False,
        null=False,
        validators=[MinValueValidator(0.0001)],
        help_text="Factor de conversión entre UOM compra y venta (requerido, default: 1)"
    )
    costo_estandar = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text="Costo estándar del producto"
    )
    costo_promedio = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        default=0.0,
        editable=False,
        help_text="Costo promedio (calculado, solo lectura)"
    )
    precio_venta = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text="Precio de venta del producto"
    )
    impuesto_iva = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=19.0,
        blank=False,
        null=False,
        validators=[MinValueValidator(0)],
        help_text="Porcentaje de IVA (requerido, ej: 19%)"
    )
    
    # --- 3. Stock y control (según especificación) ---
    stock_minimo = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=0,
        blank=False,
        null=False,
        validators=[MinValueValidator(0)],
        help_text="Stock mínimo requerido (requerido, default: 0)"
    )
    stock_maximo = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text="Stock máximo permitido"
    )
    punto_reorden = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text="Punto de reorden (si no se especifica, usar stock_minimo)"
    )
    perishable = models.BooleanField(
        default=False,
        blank=False,
        null=False,
        help_text="Producto perecedero (requerido, default: False)"
    )
    control_por_lote = models.BooleanField(
        default=False,
        blank=False,
        null=False,
        help_text="Control de inventario por lotes (requerido, default: False)"
    )
    control_por_serie = models.BooleanField(
        default=False,
        blank=False,
        null=False,
        help_text="Control de inventario por series (requerido, default: False)"
    )
    
    # --- 4. Relaciones y soporte (según especificación) ---
    imagen_url = models.URLField(
        blank=True,
        null=True,
        max_length=500,
        help_text="URL de la imagen del producto"
    )
    ficha_tecnica_url = models.URLField(
        blank=True,
        null=True,
        max_length=500,
        help_text="URL de la ficha técnica del producto"
    )
    
    # Campos adicionales para compatibilidad
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.sku})"
    
    def save(self, *args, **kwargs):
        # Generar SKU automáticamente si no se proporciona
        if not self.sku:
            # Obtener el último número de producto
            last_product = Product.objects.order_by('-id').first()
            if last_product:
                # Intentar extraer el número del último SKU
                try:
                    last_number = int(last_product.sku.split('-')[-1]) if '-' in last_product.sku else 0
                except (ValueError, AttributeError):
                    last_number = 0
                next_number = last_number + 1
            else:
                next_number = 1
            
            # Generar SKU con formato PROD-XXXX
            self.sku = f"PROD-{next_number:04d}"
            
            # Asegurar que el SKU sea único
            counter = 1
            original_sku = self.sku
            while Product.objects.filter(sku=self.sku).exclude(pk=self.pk).exists():
                self.sku = f"{original_sku}-{counter}"
                counter += 1
        
        super().save(*args, **kwargs)
    
    @property
    def supplier_preferente(self):
        """Retorna el proveedor preferente del producto"""
        try:
            preferred = self.supplier_relations.filter(preferente=True).first()
            if preferred:
                return preferred.supplier
            # Si no hay preferente, retornar el primero
            first_rel = self.supplier_relations.first()
            return first_rel.supplier if first_rel else None
        except:
            return None
    
    @property
    def total_quantity(self):
        """Stock actual total (calculado desde Inventory)"""
        result = self.stock.aggregate(total=Sum('quantity'))
        return result['total'] or 0
    
    @property
    def stock_actual(self):
        """Alias para total_quantity (compatibilidad)"""
        return self.total_quantity
    
    @property
    def alerta_bajo_stock(self):
        """Indica si el stock está por debajo del mínimo"""
        stock_actual = self.total_quantity
        punto_reorden = self.punto_reorden if self.punto_reorden is not None else self.stock_minimo
        return stock_actual < punto_reorden
    
    @property
    def alerta_por_vencer(self):
        """Indica si hay productos próximos a vencer (si es perecedero)"""
        if not self.perishable:
            return False
        # TODO: Implementar lógica cuando se agregue el modelo de lotes con fechas
        return False
    
    def get_punto_reorden_efectivo(self):
        """Retorna el punto de reorden efectivo (punto_reorden o stock_minimo)"""
        return self.punto_reorden if self.punto_reorden is not None else self.stock_minimo
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['name']
        indexes = [
            models.Index(fields=['is_active', 'name']),  # Índice compuesto para listado
            models.Index(fields=['is_active', 'categoria']),  # Índice para filtros por categoría
            models.Index(fields=['is_active', 'precio_venta']),  # Índice para ordenamiento por precio
        ]
