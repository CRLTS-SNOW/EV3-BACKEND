# gestion/management/commands/sync_firebase_users.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from gestion.firebase_service import sync_django_user_to_firebase, initialize_firebase


class Command(BaseCommand):
    help = 'Sincroniza usuarios de Django con Firebase Authentication'

    def add_arguments(self, parser):
        parser.add_argument(
            '--password',
            type=str,
            default='123',
            help='Contraseña a usar para usuarios que no tienen contraseña en Firebase (default: 123)'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Sincronizar todos los usuarios, incluso si ya existen en Firebase'
        )

    def handle(self, *args, **options):
        initialize_firebase()
        
        self.stdout.write('Sincronizando usuarios con Firebase Authentication...')
        
        users = User.objects.all()
        success_count = 0
        error_count = 0
        skip_count = 0
        
        for user in users:
            try:
                # Obtener o establecer contraseña
                password = options['password']
                
                # Si el usuario no tiene email, saltarlo
                if not user.email:
                    self.stdout.write(
                        self.style.WARNING(f'ADVERTENCIA: Usuario {user.username} no tiene email, saltando...')
                    )
                    skip_count += 1
                    continue
                
                # Sincronizar usuario
                firebase_user = sync_django_user_to_firebase(user, password=password)
                
                if firebase_user:
                    self.stdout.write(
                        self.style.SUCCESS(f'OK: Usuario {user.username} sincronizado con Firebase (UID: {firebase_user.uid})')
                    )
                    success_count += 1
                else:
                    self.stdout.write(
                        self.style.ERROR(f'ERROR: No se pudo sincronizar usuario {user.username}')
                    )
                    error_count += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'ERROR: Error al procesar usuario {user.username}: {e}')
                )
                error_count += 1
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Sincronizacion completada:'))
        self.stdout.write(f'   - Exitosos: {success_count}')
        self.stdout.write(f'   - Errores: {error_count}')
        self.stdout.write(f'   - Omitidos: {skip_count}')

