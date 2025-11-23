#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

admin = User.objects.filter(username='admin').first()
if admin:
    print(f'Usuario existe: True')
    print(f'Usuario activo: {admin.is_active}')
    print(f'Email: {admin.email}')
    print(f'Es superuser: {admin.is_superuser}')
    print(f'Tiene password: {bool(admin.password)}')
else:
    print('Usuario existe: False')

