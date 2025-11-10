# gestion/models/user_profile.py
from django.db import models
from django.contrib.auth.models import User
from .warehouse import Warehouse # Importamos el modelo Warehouse
from PIL import Image
import os

def user_photo_upload_path(instance, filename):
    """Genera la ruta para guardar la foto del usuario"""
    ext = filename.split('.')[-1]
    filename = f"{instance.user.username}_photo.{ext}"
    return f"users/photos/{filename}"

class UserProfile(models.Model):
    
    # --- Definimos los 3 roles que pediste ---
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('bodega', 'Operador de Bodega'),
        ('ventas', 'Operador de Ventas'),
    ]

    # Conecta con el usuario de Django
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Campo para guardar el ROL
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='ventas' # Por defecto, es vendedor
    )
    
    # Campo clave para el "Operador de Bodega"
    warehouse = models.ForeignKey(
        Warehouse, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Bodega asignada (solo para rol 'Operador de Bodega')"
    )
    
    # Nuevos campos: teléfono y foto
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Número de teléfono del usuario"
    )
    
    photo = models.ImageField(
        upload_to=user_photo_upload_path,
        blank=True,
        null=True,
        help_text="Foto del usuario (tamaño recomendado: 200x200px)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Devuelve ej: "xd (Administrador)"
        return f"{self.user.username} ({self.get_role_display()})"
    
    def save(self, *args, **kwargs):
        """Redimensiona la foto a un tamaño estándar antes de guardar"""
        super().save(*args, **kwargs)
        if self.photo:
            try:
                img = Image.open(self.photo.path)
                # Tamaño estándar: 200x200px
                if img.height > 200 or img.width > 200:
                    output_size = (200, 200)
                    img.thumbnail(output_size, Image.Resampling.LANCZOS)
                    img.save(self.photo.path)
            except Exception as e:
                # Si hay un error al procesar la imagen, simplemente continuamos
                pass