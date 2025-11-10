# gestion/management/commands/sync_user_firebase.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from gestion.firebase_service import sync_django_user_to_firebase, get_firebase_user_by_email, create_firebase_user, initialize_firebase


class Command(BaseCommand):
    help = 'Sincroniza un usuario específico con Firebase'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username del usuario a sincronizar')
        parser.add_argument(
            '--password',
            type=str,
            default='123456',
            help='Contraseña para crear el usuario en Firebase (default: 123456)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar creación del usuario incluso si ya existe'
        )

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        force = options['force']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Usuario "{username}" no encontrado en Django.'))
            return

        self.stdout.write(f'Sincronizando usuario: {username}')
        self.stdout.write(f'  Email: {user.email or "No tiene email"}')
        self.stdout.write(f'  Activo: {user.is_active}')
        self.stdout.write(f'  Nombre completo: {user.get_full_name() or user.username}')

        if not user.email:
            self.stdout.write(self.style.ERROR('  ERROR: El usuario no tiene email. No se puede sincronizar con Firebase.'))
            self.stdout.write(self.style.WARNING('  SOLUCIÓN: Agrega un email al usuario desde la interfaz web.'))
            return

        # Inicializar Firebase
        initialize_firebase()

        # Verificar si el usuario ya existe en Firebase
        firebase_user = get_firebase_user_by_email(user.email)
        
        if firebase_user and not force:
            self.stdout.write(self.style.WARNING(f'  El usuario ya existe en Firebase (UID: {firebase_user.uid})'))
            self.stdout.write('  Usa --force para forzar la actualización.')
            return

        # Sincronizar o crear el usuario
        if force and firebase_user:
            self.stdout.write('  Actualizando usuario existente en Firebase...')
        else:
            self.stdout.write('  Creando usuario en Firebase...')

        firebase_user = sync_django_user_to_firebase(user, password=password)

        if firebase_user:
            self.stdout.write(self.style.SUCCESS(f'  ¡Usuario sincronizado exitosamente!'))
            self.stdout.write(f'  UID: {firebase_user.uid}')
            self.stdout.write(f'  Email: {firebase_user.email}')
            self.stdout.write(f'  Display Name: {firebase_user.display_name}')
            self.stdout.write(f'  Disabled: {firebase_user.disabled}')
            if not force:
                self.stdout.write(self.style.SUCCESS(f'  Contraseña configurada: {password}'))
        else:
            self.stdout.write(self.style.ERROR('  ERROR: No se pudo sincronizar el usuario con Firebase.'))
            self.stdout.write(self.style.WARNING('  Verifica la configuración de Firebase en firebase-credentials.json'))

