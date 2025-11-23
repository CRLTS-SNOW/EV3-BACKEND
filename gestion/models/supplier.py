# gestion/models/supplier.py
from django.db import models
from django.core.validators import EmailValidator

class Supplier(models.Model):
    """
    Modelo de Proveedor según especificación del proyecto Lili's
    """
    
    # --- 1. Identificación legal y contacto (según especificación) ---
    rut_nif = models.CharField(
        max_length=20,
        unique=True,
        blank=False,
        null=False,
        help_text="RUT/NIF del proveedor (único, requerido)"
    )
    razon_social = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        help_text="Razón social del proveedor (requerido)"
    )
    nombre_fantasia = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Nombre de fantasía del proveedor (opcional)"
    )
    email = models.EmailField(
        max_length=254,
        validators=[EmailValidator()],
        help_text="Email de contacto del proveedor (requerido)"
    )
    telefono = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        help_text="Teléfono de contacto"
    )
    sitio_web = models.URLField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Sitio web del proveedor"
    )
    
    # --- 2. Dirección (según especificación) ---
    direccion = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Dirección del proveedor"
    )
    ciudad = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        help_text="Ciudad del proveedor"
    )
    pais = models.CharField(
        max_length=64,
        default='Chile',
        blank=False,
        null=False,
        help_text="País del proveedor (requerido, default: Chile)"
    )
    
    # --- 3. Comercial (según especificación) ---
    condiciones_pago = models.CharField(
        max_length=100,
        default='30 días',
        blank=False,
        null=False,
        help_text="Condiciones de pago (ej: 30 días, contado, etc., requerido)"
    )
    moneda = models.CharField(
        max_length=8,
        default='CLP',
        blank=False,
        null=False,
        help_text="Moneda de transacción (ej: CLP, USD, requerido)"
    )
    contacto_principal_nombre = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        help_text="Nombre del contacto principal"
    )
    contacto_principal_email = models.EmailField(
        max_length=254,
        blank=True,
        null=True,
        help_text="Email del contacto principal"
    )
    contacto_principal_telefono = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        help_text="Teléfono del contacto principal"
    )
    estado = models.CharField(
        max_length=20,
        choices=[
            ('ACTIVO', 'Activo'),
            ('BLOQUEADO', 'Bloqueado'),
        ],
        default='ACTIVO',
        blank=False,
        null=False,
        help_text="Estado del proveedor (requerido)"
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        max_length=1000,
        help_text="Observaciones adicionales (máximo 1000 caracteres)"
    )
    
    # Campos adicionales para compatibilidad
    name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Nombre del proveedor (compatibilidad, usar razon_social)"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.razon_social or self.name or f"Proveedor {self.rut_nif}"
    
    def save(self, *args, **kwargs):
        # Mantener compatibilidad con campo 'name'
        if not self.name:
            self.name = self.razon_social
        super().save(*args, **kwargs)
    
    @property
    def nombre_display(self):
        """Retorna el nombre a mostrar (nombre_fantasia o razon_social)"""
        return self.nombre_fantasia or self.razon_social
    
    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['razon_social']
