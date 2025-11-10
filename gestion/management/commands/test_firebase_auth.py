# gestion/management/commands/test_firebase_auth.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from gestion.firebase_service import verify_firebase_password, get_firebase_user_by_email, initialize_firebase

class Command(BaseCommand):
    help = 'Prueba la autenticación con Firebase para un usuario específico'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username o email del usuario a probar')
        parser.add_argument('password', type=str, help='Contraseña a probar')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        
        self.stdout.write(f'Probando autenticación para: {username}')
        self.stdout.write('=' * 50)
        
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
                self.stdout.write(self.style.ERROR(f'❌ Usuario no encontrado en Django: {username}'))
                return
            
            self.stdout.write(self.style.SUCCESS(f'✅ Usuario encontrado en Django:'))
            self.stdout.write(f'   Username: {user.username}')
            self.stdout.write(f'   Email: {user.email}')
            self.stdout.write(f'   Activo: {user.is_active}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error al buscar usuario: {e}'))
            return
        
        # Verificar si tiene email
        if not user.email:
            self.stdout.write(self.style.ERROR('❌ El usuario no tiene email configurado'))
            return
        
        # Normalizar email
        email = user.email.strip().lower()
        self.stdout.write(f'   Email normalizado: {email}')
        
        # Inicializar Firebase
        self.stdout.write('\nInicializando Firebase...')
        initialize_firebase()
        
        # Verificar si el usuario existe en Firebase
        self.stdout.write(f'\nBuscando usuario en Firebase con email: {email}')
        firebase_user = get_firebase_user_by_email(email)
        
        if firebase_user:
            self.stdout.write(self.style.SUCCESS('✅ Usuario encontrado en Firebase:'))
            self.stdout.write(f'   UID: {firebase_user.uid}')
            self.stdout.write(f'   Email: {firebase_user.email}')
            self.stdout.write(f'   Display Name: {firebase_user.display_name}')
            self.stdout.write(f'   Disabled: {firebase_user.disabled}')
        else:
            self.stdout.write(self.style.ERROR('❌ Usuario NO encontrado en Firebase'))
            self.stdout.write('   El usuario necesita ser sincronizado con Firebase')
            return
        
        # Probar autenticación
        self.stdout.write(f'\nProbando autenticación con contraseña...')
        result = verify_firebase_password(email, password)
        
        if result.get('success'):
            self.stdout.write(self.style.SUCCESS('✅ Autenticación EXITOSA'))
            self.stdout.write(f'   UID: {result.get("uid")}')
            self.stdout.write(f'   Email: {result.get("email")}')
        else:
            self.stdout.write(self.style.ERROR('❌ Autenticación FALLIDA'))
            error = result.get('error', 'Error desconocido')
            error_code = result.get('error_code', 'N/A')
            self.stdout.write(f'   Error: {error}')
            self.stdout.write(f'   Código: {error_code}')
            
            # Sugerencias
            self.stdout.write('\n💡 Posibles causas:')
            self.stdout.write('   1. La contraseña es incorrecta')
            self.stdout.write('   2. El usuario cambió la contraseña pero Firebase aún no la ha actualizado')
            self.stdout.write('   3. Hay un problema con la API key de Firebase')
            self.stdout.write('   4. El email en Django no coincide exactamente con el email en Firebase')

