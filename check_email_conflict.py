#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from gestion.firebase_service import get_firebase_user_by_email, initialize_firebase
from django.contrib.auth import get_user_model

User = get_user_model()

initialize_firebase()

email_to_check = 'carlos.vivanco.08@gmail.com'

print(f"=== Verificando email: {email_to_check} ===\n")

# Verificar en Django
django_users = User.objects.filter(email__iexact=email_to_check)
print(f"Usuarios en Django con este email: {django_users.count()}")
for user in django_users:
    print(f"  - Username: {user.username}, ID: {user.id}, Activo: {user.is_active}")

# Verificar en Firebase
firebase_user = get_firebase_user_by_email(email_to_check)
if firebase_user:
    print(f"\nUsuario en Firebase:")
    print(f"  - Email: {firebase_user.email}")
    print(f"  - UID: {firebase_user.uid}")
    print(f"  - Display Name: {firebase_user.display_name}")
    print(f"  - Deshabilitado: {firebase_user.disabled}")
else:
    print(f"\n❌ No hay usuario en Firebase con este email")

# Verificar usuario admin
print(f"\n=== Verificando usuario admin ===")
admin_user = User.objects.filter(username='admin').first()
if admin_user:
    print(f"Usuario admin en Django:")
    print(f"  - Username: {admin_user.username}")
    print(f"  - Email: {admin_user.email}")
    print(f"  - ID: {admin_user.id}")
    
    # Verificar en Firebase
    if admin_user.email:
        admin_firebase = get_firebase_user_by_email(admin_user.email)
        if admin_firebase:
            print(f"\nUsuario admin en Firebase:")
            print(f"  - Email: {admin_firebase.email}")
            print(f"  - UID: {admin_firebase.uid}")
            print(f"  - Display Name: {admin_firebase.display_name}")
        else:
            print(f"\n❌ Usuario admin NO encontrado en Firebase con email {admin_user.email}")

