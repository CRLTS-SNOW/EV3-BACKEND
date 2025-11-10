# gestion/models/warehouse.py
from django.db import models

class Warehouse(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name