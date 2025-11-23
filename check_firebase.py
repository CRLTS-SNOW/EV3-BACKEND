#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from gestion.firebase_service import get_firebase_user_by_email, verify_firebase_password, initialize_firebase
from django.contrib.auth import get_user_model

User = get_user_model()

print("=== Verificando Firebase ===")
initialize_firebase()

# Verificar usuario admin
admin_user = User.objects.filter(username='admin').first()
if admin_user:
    print(f"\nUsuario Django encontrado:")
    print(f"  Username: {admin_user.username}")
    print(f"  Email: {admin_user.email}")
    print(f"  Activo: {admin_user.is_active}")
    
    # Verificar en Firebase
    firebase_user = get_firebase_user_by_email(admin_user.email)
    if firebase_user:
        print(f"\nUsuario Firebase encontrado:")
        print(f"  Email: {firebase_user.email}")
        print(f"  UID: {firebase_user.uid}")
        print(f"  Deshabilitado: {firebase_user.disabled}")
    else:
        print(f"\n❌ Usuario NO encontrado en Firebase")
        print("  Necesitas crear el usuario en Firebase o sincronizarlo")
    
    # Probar autenticación
    print(f"\n=== Probando autenticación ===")
    result = verify_firebase_password(admin_user.email, '123456')
    if result.get('success'):
        print("✅ Autenticación exitosa con contraseña '123456'")
    else:
        print(f"❌ Error en autenticación: {result.get('error', 'Error desconocido')}")
else:
    print("❌ Usuario 'admin' no encontrado en Django")

