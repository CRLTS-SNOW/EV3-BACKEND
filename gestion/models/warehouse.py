# gestion/models/warehouse.py
from django.db import models

class Warehouse(models.Model):
    name = models.CharField(
        max_length=200,
        blank=False,
        null=False,
        help_text="Nombre de la bodega (requerido)"
    )
    address = models.TextField(
        blank=False,
        null=False,
        max_length=500,
        help_text="Dirección de la bodega (requerido, máximo 500 caracteres)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indica si la bodega está activa"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Bodega"
        verbose_name_plural = "Bodegas"
        ordering = ['name']