# gestion/models/zone.py
from django.db import models
from .warehouse import Warehouse # Importacion relativa

class Zone(models.Model):
    name = models.CharField(max_length=100)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='zones')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (in {self.warehouse.name})"