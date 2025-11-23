# gestion/models/client.py
from django.db import models
from django.core.validators import EmailValidator

class Client(models.Model):
    name = models.CharField(
        max_length=200, 
        blank=False,
        null=False,
        help_text="Nombre o Razón Social del cliente (requerido)"
    )
    rut = models.CharField(
        max_length=12, 
        unique=True, 
        blank=True, 
        null=True, 
        help_text="RUT del cliente (opcional, único si se proporciona)"
    )
    email = models.EmailField(
        max_length=150, 
        blank=True, 
        null=True,
        validators=[EmailValidator()],
        help_text="Email del cliente (opcional)"
    )
    phone = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        help_text="Teléfono del cliente (opcional, formato chileno)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['name']