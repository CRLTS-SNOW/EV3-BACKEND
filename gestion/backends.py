# gestion/backends.py

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.conf import settings

User = get_user_model()


class EmailOrUsernameBackend(ModelBackend):
    """
    Backend de autenticación personalizado que permite login con email o username.
    Solo verifica credenciales en Firebase, NO en Django.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Autentica un usuario usando email o username.
        Verifica las credenciales SOLO en Firebase, no en Django.
        """
        try:
            if username is None:
                username = kwargs.get('username')
            
            if username is None or password is None:
                return None
            
            # Normalizar el username/email (trim y lowercase)
            if not isinstance(username, str):
                return None
                
            username = username.strip().lower() if username else None
            
            if not username:
                return None
            
            # Obtener el email del usuario desde Django
            try:
                # Buscar por username (case-insensitive) o email (case-insensitive)
                user = User.objects.filter(
                    Q(username__iexact=username) | Q(email__iexact=username)
                ).first()
                
                if not user:
                    # Si no se encuentra, intentar búsqueda más amplia
                    user = User.objects.filter(
                        Q(username__icontains=username) | Q(email__icontains=username)
                    ).first()
            except Exception as e:
                if settings.DEBUG:
                    print(f"ERROR en autenticación: Error al buscar usuario: {e}")
                return None
            
            if not user:
                if settings.DEBUG:
                    print(f"DEBUG: Usuario no encontrado en Django: {username}")
                return None
            
            # Si el usuario no tiene email, no se puede verificar en Firebase
            if not user.email:
                if settings.DEBUG:
                    print(f"DEBUG: Usuario {user.username} no tiene email configurado")
                return None
            
            # Normalizar el email (trim y lowercase) antes de verificar en Firebase
            email = user.email.strip().lower()
            
            if not email:
                return None
            
            # Verificar credenciales SOLO en Firebase
            try:
                from gestion.firebase_service import verify_firebase_password
                firebase_result = verify_firebase_password(email, password)
            except Exception as e:
                if settings.DEBUG:
                    print(f"ERROR: Excepción al verificar contraseña en Firebase: {e}")
                # Si hay un error en Firebase, no autenticar (retornar None, no lanzar excepción)
                return None
            
            if settings.DEBUG:
                if firebase_result.get('success'):
                    print(f"DEBUG: Autenticación exitosa en Firebase para {email}")
                else:
                    error = firebase_result.get('error', 'Error desconocido')
                    print(f"DEBUG: Error en autenticación Firebase para {email}: {error}")
            
            if firebase_result and firebase_result.get('success'):
                # Las credenciales son correctas en Firebase
                # Autenticar el usuario en Django
                try:
                    # Django requiere que el usuario tenga una contraseña usable para autenticarse
                    # Por lo tanto, establecemos una contraseña dummy que nunca se usará
                    if not user.has_usable_password() or user.check_password('DUMMY_PASSWORD_NOT_USED'):
                        # Establecer una contraseña dummy en Django (nunca se usa, solo para que Django permita autenticación)
                        user.set_password('DUMMY_PASSWORD_NOT_USED_FIREBASE_ONLY')
                        user.save(update_fields=['password'])
                    
                    # Verificar que el usuario puede autenticarse
                    if user.is_active:
                        return user
                except Exception as e:
                    if settings.DEBUG:
                        print(f"ERROR: Excepción al guardar usuario: {e}")
                    return None
            
            return None
            
        except Exception as e:
            # Capturar cualquier excepción no esperada y retornar None en lugar de lanzarla
            # Esto previene que Django devuelva un error 400
            if settings.DEBUG:
                print(f"ERROR CRÍTICO en autenticación: {e}")
                import traceback
                traceback.print_exc()
            return None

