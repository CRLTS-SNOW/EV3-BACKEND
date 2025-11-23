# gestion/models/user_profile.py
from django.db import models
from django.contrib.auth.models import User
from .warehouse import Warehouse
from PIL import Image
import os

def user_photo_upload_path(instance, filename):
    """Genera la ruta para guardar la foto del usuario"""
    ext = filename.split('.')[-1]
    filename = f"{instance.user.username}_photo.{ext}"
    return f"users/photos/{filename}"

class UserProfile(models.Model):
    
    # --- Roles según especificación ---
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('bodega', 'Operador de Bodega'),
        ('ventas', 'Operador de Ventas'),
        ('auditor', 'Auditor'),
        ('operador', 'Operador'),
    ]
    
    # --- Estado según especificación ---
    STATUS_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('BLOQUEADO', 'Bloqueado'),
        ('INACTIVO', 'Inactivo'),
    ]

    # Conecta con el usuario de Django
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # --- 1. Identificación (según especificación) ---
    # username y email vienen del modelo User (requeridos, únicos)
    nombres = models.CharField(max_length=100, blank=False, null=False, help_text="Nombres del usuario (requerido)")
    apellidos = models.CharField(max_length=100, blank=False, null=False, help_text="Apellidos del usuario (requerido)")
    phone = models.CharField(max_length=20, blank=True, null=True, help_text="Número de teléfono del usuario (opcional)")
    
    # --- 2. Estado y acceso (según especificación) ---
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='ventas',
        blank=False,
        null=False,
        help_text="Rol del usuario en el sistema (requerido)"
    )
    estado = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVO',
        blank=False,
        null=False,
        help_text="Estado del usuario (requerido, default: ACTIVO)"
    )
    mfa_habilitado = models.BooleanField(
        default=False,
        blank=False,
        null=False,
        help_text="Multi-factor authentication habilitado (requerido, default: False)"
    )
    ultimo_acceso = models.DateTimeField(
        blank=True,
        null=True,
        editable=False,
        help_text="Última vez que el usuario accedió al sistema (solo lectura)"
    )
    sesiones_activas = models.IntegerField(
        default=0,
        editable=False,
        help_text="Número de sesiones activas (solo lectura)"
    )
    
    # --- 3. Metadatos (según especificación) ---
    area = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Área o unidad del usuario"
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        help_text="Observaciones adicionales sobre el usuario"
    )
    
    # Campo clave para el "Operador de Bodega"
    warehouse = models.ForeignKey(
        Warehouse, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Bodega asignada (solo para rol 'Operador de Bodega')"
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
        nombre_completo = f"{self.nombres or ''} {self.apellidos or ''}".strip()
        if nombre_completo:
            return f"{nombre_completo} ({self.get_role_display()})"
        return f"{self.user.username} ({self.get_role_display()})"
    
    @property
    def nombre_completo(self):
        """Retorna el nombre completo del usuario"""
        nombre = f"{self.nombres or ''} {self.apellidos or ''}".strip()
        return nombre if nombre else self.user.username
    
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
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"