# gestion/models/client.py
from django.db import models

class Client(models.Model):
    name = models.CharField(max_length=200, help_text="Nombre o Razón Social del cliente")
    rut = models.CharField(max_length=12, unique=True, blank=True, null=True, help_text="RUT del cliente (opcional)")
    email = models.EmailField(max_length=150, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name