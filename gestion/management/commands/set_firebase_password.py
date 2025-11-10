# gestion/management/commands/set_firebase_password.py

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from gestion.firebase_service import get_firebase_user_by_email, update_firebase_user, initialize_firebase

class Command(BaseCommand):
    help = 'Establece o actualiza la contraseña de un usuario en Firebase'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username o email del usuario')
        parser.add_argument('password', type=str, help='Nueva contraseña (mínimo 6 caracteres)')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        
        if len(password) < 6:
            raise CommandError('La contraseña debe tener al menos 6 caracteres')
        
        self.stdout.write(f'Buscando usuario: {username}')
        
        # Buscar usuario en Django
        try:
            user = User.objects.filter(
                username__iexact=username
            ).first()
            
            if not user:
                user = User.objects.filter(
                    email__iexact=username
                ).first()
            
            if not user:
                raise CommandError(f'Usuario no encontrado en Django: {username}')
            
            self.stdout.write(self.style.SUCCESS(f'✅ Usuario encontrado en Django:'))
            self.stdout.write(f'   Username: {user.username}')
            self.stdout.write(f'   Email: {user.email}')
        except Exception as e:
            raise CommandError(f'Error al buscar usuario: {e}')
        
        # Verificar si tiene email
        if not user.email:
            raise CommandError(f'El usuario {user.username} no tiene email configurado')
        
        # Normalizar email
        email = user.email.strip().lower()
        
        # Inicializar Firebase
        self.stdout.write('\nInicializando Firebase...')
        initialize_firebase()
        
        # Buscar usuario en Firebase
        self.stdout.write(f'Buscando usuario en Firebase con email: {email}')
        firebase_user = get_firebase_user_by_email(email)
        
        if not firebase_user:
            raise CommandError(f'Usuario no encontrado en Firebase. Ejecuta: python manage.py sync_user_firebase {user.username} --password {password}')
        
        self.stdout.write(self.style.SUCCESS(f'✅ Usuario encontrado en Firebase:'))
        self.stdout.write(f'   UID: {firebase_user.uid}')
        self.stdout.write(f'   Email: {firebase_user.email}')
        
        # Actualizar contraseña en Firebase
        self.stdout.write(f'\nActualizando contraseña en Firebase...')
        try:
            updated_user = update_firebase_user(firebase_user.uid, password=password)
            if updated_user:
                self.stdout.write(self.style.SUCCESS('✅ Contraseña actualizada exitosamente en Firebase'))
                self.stdout.write(f'\nAhora el usuario {user.username} puede iniciar sesión con:')
                self.stdout.write(f'   Username: {user.username}')
                self.stdout.write(f'   Email: {user.email}')
                self.stdout.write(f'   Contraseña: {password}')
            else:
                raise CommandError('No se pudo actualizar la contraseña en Firebase')
        except Exception as e:
            raise CommandError(f'Error al actualizar contraseña en Firebase: {e}')

