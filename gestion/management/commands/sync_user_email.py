# gestion/management/commands/sync_user_email.py

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from gestion.firebase_service import get_firebase_user_by_email, update_firebase_user, create_firebase_user, initialize_firebase

class Command(BaseCommand):
    help = 'Sincroniza el email de un usuario entre Django y Firebase'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username del usuario a sincronizar')
        parser.add_argument('--create-if-not-exists', action='store_true', help='Crear usuario en Firebase si no existe')

    def handle(self, *args, **options):
        username = options['username']
        create_if_not_exists = options.get('create_if_not_exists', False)
        
        self.stdout.write(f'Sincronizando usuario: {username}')
        self.stdout.write('=' * 50)
        
        # Buscar usuario en Django
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f'Usuario "{username}" no encontrado en Django')
        
        if not user.email:
            raise CommandError(f'El usuario "{username}" no tiene email configurado')
        
        email = user.email.strip().lower()
        self.stdout.write(f'Email en Django: {email}')
        
        # Inicializar Firebase
        initialize_firebase()
        
        # Buscar usuario en Firebase
        firebase_user = get_firebase_user_by_email(email)
        
        if firebase_user:
            self.stdout.write(self.style.SUCCESS('✅ Usuario encontrado en Firebase:'))
            self.stdout.write(f'   UID: {firebase_user.uid}')
            self.stdout.write(f'   Email: {firebase_user.email}')
            self.stdout.write(f'   Display Name: {firebase_user.display_name}')
            
            # Verificar si el email coincide
            if firebase_user.email.lower() != email:
                self.stdout.write(self.style.WARNING('⚠️  El email en Firebase no coincide con Django'))
                self.stdout.write(f'   Actualizando email en Firebase...')
                try:
                    updated_user = update_firebase_user(
                        firebase_user.uid,
                        email=email,
                        display_name=user.get_full_name() or user.username,
                        disabled=not user.is_active
                    )
                    if updated_user:
                        self.stdout.write(self.style.SUCCESS('✅ Email actualizado en Firebase'))
                    else:
                        raise CommandError('No se pudo actualizar el email en Firebase')
                except Exception as e:
                    raise CommandError(f'Error al actualizar email en Firebase: {e}')
            else:
                # Solo actualizar display_name y disabled si es necesario
                try:
                    update_firebase_user(
                        firebase_user.uid,
                        display_name=user.get_full_name() or user.username,
                        disabled=not user.is_active
                    )
                    self.stdout.write(self.style.SUCCESS('✅ Usuario sincronizado correctamente'))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'⚠️  No se pudo actualizar datos: {e}'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  Usuario NO encontrado en Firebase'))
            
            if create_if_not_exists:
                self.stdout.write('Creando usuario en Firebase...')
                default_password = '123456'  # Contraseña temporal
                try:
                    firebase_user = create_firebase_user(
                        email=email,
                        password=default_password,
                        display_name=user.get_full_name() or user.username,
                        disabled=not user.is_active
                    )
                    if firebase_user:
                        self.stdout.write(self.style.SUCCESS('✅ Usuario creado en Firebase'))
                        self.stdout.write(f'   UID: {firebase_user.uid}')
                        self.stdout.write(f'   Contraseña temporal: {default_password}')
                        self.stdout.write(self.style.WARNING('⚠️  El usuario debe cambiar la contraseña después del primer login'))
                    else:
                        raise CommandError('No se pudo crear el usuario en Firebase')
                except Exception as e:
                    error_msg = str(e)
                    if 'EMAIL_EXISTS' in error_msg:
                        # El email ya existe con otro usuario
                        self.stdout.write(self.style.ERROR('❌ El email ya existe en Firebase con otro usuario'))
                        raise CommandError('El email ya está en uso por otro usuario en Firebase')
                    else:
                        raise CommandError(f'Error al crear usuario en Firebase: {e}')
            else:
                self.stdout.write(self.style.ERROR('❌ Usuario no encontrado en Firebase'))
                self.stdout.write('   Usa --create-if-not-exists para crear el usuario en Firebase')
                raise CommandError('Usuario no encontrado en Firebase. Usa --create-if-not-exists para crearlo.')

