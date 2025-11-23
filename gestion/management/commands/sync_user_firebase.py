# gestion/management/commands/sync_user_firebase.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from gestion.firebase_service import get_firebase_user_by_email, sync_django_user_to_firebase, initialize_firebase

class Command(BaseCommand):
    help = 'Sincroniza un usuario específico con Firebase o verifica su estado'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username del usuario a sincronizar',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email del usuario a sincronizar',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Sincronizar todos los usuarios con email',
        )
        parser.add_argument(
            '--check',
            action='store_true',
            help='Solo verificar estado sin sincronizar',
        )

    def handle(self, *args, **options):
        initialize_firebase()
        
        username = options.get('username')
        email = options.get('email')
        sync_all = options.get('all', False)
        check_only = options.get('check', False)
        
        if sync_all:
            # Sincronizar todos los usuarios con email
            users = User.objects.filter(email__isnull=False).exclude(email='')
            self.stdout.write(f'Sincronizando {users.count()} usuarios con Firebase...')
            
            for user in users:
                self.sync_user(user, check_only)
        elif username:
            try:
                user = User.objects.get(username=username)
                self.sync_user(user, check_only)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Usuario "{username}" no encontrado'))
        elif email:
            try:
                user = User.objects.get(email=email)
                self.sync_user(user, check_only)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Usuario con email "{email}" no encontrado'))
        else:
            self.stdout.write(self.style.ERROR('Debes especificar --username, --email o --all'))
            self.stdout.write('Ejemplo: python manage.py sync_user_firebase --username admin')
            self.stdout.write('Ejemplo: python manage.py sync_user_firebase --email tu@email.com')
            self.stdout.write('Ejemplo: python manage.py sync_user_firebase --all')
    
    def sync_user(self, user, check_only=False):
        self.stdout.write(f'\n--- Usuario: {user.username} ---')
        self.stdout.write(f'Email Django: {user.email}')
        
        if not user.email:
            self.stdout.write(self.style.WARNING('  Usuario sin email, no se puede sincronizar'))
            return
        
        # Verificar si existe en Firebase
        firebase_user = get_firebase_user_by_email(user.email)
        
        if firebase_user:
            self.stdout.write(self.style.SUCCESS(f'  Usuario encontrado en Firebase'))
            self.stdout.write(f'  UID: {firebase_user.uid}')
            self.stdout.write(f'  Email Firebase: {firebase_user.email}')
            self.stdout.write(f'  Email verificado: {firebase_user.email_verified}')
            self.stdout.write(f'  Deshabilitado: {firebase_user.disabled}')
            
            if firebase_user.email.strip().lower() != user.email.strip().lower():
                self.stdout.write(self.style.WARNING(f'  ADVERTENCIA: El email en Firebase ({firebase_user.email}) no coincide con Django ({user.email})'))
            
            if check_only:
                return
            
            # Sincronizar
            self.stdout.write('  Sincronizando...')
            result = sync_django_user_to_firebase(user, password=None, old_email=None)
            if result:
                self.stdout.write(self.style.SUCCESS('  Sincronización exitosa'))
            else:
                self.stdout.write(self.style.ERROR('  Error en la sincronización'))
        else:
            self.stdout.write(self.style.WARNING('  Usuario NO encontrado en Firebase'))
            
            if check_only:
                self.stdout.write('  Usa --sync para crear el usuario en Firebase')
                return
            
            # Crear en Firebase
            self.stdout.write('  Creando usuario en Firebase...')
            result = sync_django_user_to_firebase(user, password=None, old_email=None)
            if result:
                self.stdout.write(self.style.SUCCESS('  Usuario creado en Firebase exitosamente'))
                self.stdout.write(f'  UID: {result.uid}')
                self.stdout.write(self.style.WARNING('  NOTA: El usuario necesitará usar "Olvidé mi contraseña" para establecer una contraseña'))
            else:
                self.stdout.write(self.style.ERROR('  Error al crear usuario en Firebase'))
