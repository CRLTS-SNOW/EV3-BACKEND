# gestion/models/zone.py
from django.db import models
from .warehouse import Warehouse # Importacion relativa

class Zone(models.Model):
    name = models.CharField(
        max_length=100,
        blank=False,
        null=False,
        help_text="Nombre de la zona (requerido)"
    )
    warehouse = models.ForeignKey(
        Warehouse, 
        on_delete=models.CASCADE, 
        related_name='zones',
        help_text="Bodega a la que pertenece la zona (requerido)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indica si la zona está activa"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (in {self.warehouse.name})"
    
    class Meta:
        verbose_name = "Zona"
        verbose_name_plural = "Zonas"
        ordering = ['warehouse', 'name']