# gestion/management/commands/reset_demo_users.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from gestion.models import UserProfile, Warehouse
from gestion.firebase_service import sync_django_user_to_firebase


class Command(BaseCommand):
    help = 'Restablece las credenciales de usuario demo (admin, bodeguero, vendedor)'

    def handle(self, *args, **options):
        # Contraseña por defecto para todos
        default_password = '123456'
        
        # Obtener o crear la primera bodega para el bodeguero
        warehouse, _ = Warehouse.objects.get_or_create(
            name='Bodega Principal',
            defaults={'is_active': True}
        )
        
        # 1. Usuario Admin
        try:
            admin_user = User.objects.get(username='admin')
            admin_user.email = 'admin@lilis.com'
            admin_user.first_name = 'Administrador'
            admin_user.last_name = 'Sistema'
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.is_active = True
            admin_user.save()
            created = False
        except User.DoesNotExist:
            admin_user = User.objects.create_user(
                username='admin',
                email='admin@lilis.com',
                password=default_password,
                first_name='Administrador',
                last_name='Sistema',
                is_staff=True,
                is_superuser=True,
                is_active=True
            )
            created = True
        
        admin_profile, _ = UserProfile.objects.get_or_create(
            user=admin_user,
            defaults={
                'role': 'admin',
                'nombres': 'Administrador',
                'apellidos': 'Sistema',
                'estado': 'ACTIVO',
                'mfa_habilitado': False,
                'area': 'Administración'
            }
        )
        if not _:
            admin_profile.role = 'admin'
            admin_profile.nombres = 'Administrador'
            admin_profile.apellidos = 'Sistema'
            admin_profile.estado = 'ACTIVO'
            admin_profile.mfa_habilitado = False
            admin_profile.area = 'Administración'
            admin_profile.save()
        
        # Sincronizar con Firebase
        try:
            sync_django_user_to_firebase(admin_user, password=default_password)
            self.stdout.write(self.style.SUCCESS(f'✓ Usuario admin creado/actualizado y sincronizado con Firebase'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠ Usuario admin creado/actualizado pero error en Firebase: {e}'))
        
        # 2. Usuario Bodeguero
        try:
            bodeguero_user = User.objects.get(username='bodeguero')
            bodeguero_user.email = 'bodeguero@lilis.com'
            bodeguero_user.first_name = 'Operador'
            bodeguero_user.last_name = 'Bodega'
            bodeguero_user.is_active = True
            bodeguero_user.save()
            created = False
        except User.DoesNotExist:
            bodeguero_user = User.objects.create_user(
                username='bodeguero',
                email='bodeguero@lilis.com',
                password=default_password,
                first_name='Operador',
                last_name='Bodega',
                is_active=True
            )
            created = True
        
        bodeguero_profile, _ = UserProfile.objects.get_or_create(
            user=bodeguero_user,
            defaults={
                'role': 'bodega',
                'nombres': 'Operador',
                'apellidos': 'Bodega',
                'estado': 'ACTIVO',
                'mfa_habilitado': False,
                'area': 'Bodega',
                'warehouse': warehouse
            }
        )
        if not _:
            bodeguero_profile.role = 'bodega'
            bodeguero_profile.nombres = 'Operador'
            bodeguero_profile.apellidos = 'Bodega'
            bodeguero_profile.estado = 'ACTIVO'
            bodeguero_profile.mfa_habilitado = False
            bodeguero_profile.area = 'Bodega'
            bodeguero_profile.warehouse = warehouse
            bodeguero_profile.save()
        
        # Sincronizar con Firebase
        try:
            sync_django_user_to_firebase(bodeguero_user, password=default_password)
            self.stdout.write(self.style.SUCCESS(f'✓ Usuario bodeguero creado/actualizado y sincronizado con Firebase'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠ Usuario bodeguero creado/actualizado pero error en Firebase: {e}'))
        
        # 3. Usuario Vendedor
        try:
            vendedor_user = User.objects.get(username='vendedor')
            vendedor_user.email = 'vendedor@lilis.com'
            vendedor_user.first_name = 'Operador'
            vendedor_user.last_name = 'Ventas'
            vendedor_user.is_active = True
            vendedor_user.save()
            created = False
        except User.DoesNotExist:
            vendedor_user = User.objects.create_user(
                username='vendedor',
                email='vendedor@lilis.com',
                password=default_password,
                first_name='Operador',
                last_name='Ventas',
                is_active=True
            )
            created = True
        
        vendedor_profile, _ = UserProfile.objects.get_or_create(
            user=vendedor_user,
            defaults={
                'role': 'ventas',
                'nombres': 'Operador',
                'apellidos': 'Ventas',
                'estado': 'ACTIVO',
                'mfa_habilitado': False,
                'area': 'Ventas'
            }
        )
        if not _:
            vendedor_profile.role = 'ventas'
            vendedor_profile.nombres = 'Operador'
            vendedor_profile.apellidos = 'Ventas'
            vendedor_profile.estado = 'ACTIVO'
            vendedor_profile.mfa_habilitado = False
            vendedor_profile.area = 'Ventas'
            vendedor_profile.save()
        
        # Sincronizar con Firebase
        try:
            sync_django_user_to_firebase(vendedor_user, password=default_password)
            self.stdout.write(self.style.SUCCESS(f'✓ Usuario vendedor creado/actualizado y sincronizado con Firebase'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠ Usuario vendedor creado/actualizado pero error en Firebase: {e}'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Credenciales demo restablecidas correctamente'))
        self.stdout.write(self.style.SUCCESS('\nCredenciales:'))
        self.stdout.write(self.style.SUCCESS('  - Admin: admin / 123456'))
        self.stdout.write(self.style.SUCCESS('  - Bodeguero: bodeguero / 123456'))
        self.stdout.write(self.style.SUCCESS('  - Vendedor: vendedor / 123456'))
