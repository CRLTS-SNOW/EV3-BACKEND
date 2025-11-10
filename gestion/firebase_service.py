# gestion/firebase_service.py

import os
import firebase_admin
from firebase_admin import credentials, auth
from django.conf import settings
from decouple import config
import requests

# Variable global para verificar si Firebase está inicializado
_firebase_initialized = False

def initialize_firebase():
    """
    Inicializa Firebase Admin SDK.
    """
    global _firebase_initialized
    
    if _firebase_initialized:
        return
    
    try:
        # Opción 1: Usar archivo de credenciales (recomendado para producción)
        # Debes descargar el archivo de credenciales desde Firebase Console
        # y guardarlo como 'firebase-credentials.json' en la raíz del proyecto
        cred_path = os.path.join(settings.BASE_DIR, 'firebase-credentials.json')
        
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            _firebase_initialized = True
            return
        
        # Opción 2: Usar variables de entorno (para desarrollo)
        # Configurar las siguientes variables de entorno o en .env:
        # FIREBASE_PROJECT_ID, FIREBASE_PRIVATE_KEY, FIREBASE_CLIENT_EMAIL
        project_id = config('FIREBASE_PROJECT_ID', default='backend-proyecto-lilis')
        private_key = config('FIREBASE_PRIVATE_KEY', default=None)
        client_email = config('FIREBASE_CLIENT_EMAIL', default=None)
        
        if private_key and client_email:
            # Reemplazar \\n por \n en la clave privada
            private_key = private_key.replace('\\n', '\n')
            
            cred = credentials.Certificate({
                "type": "service_account",
                "project_id": project_id,
                "private_key_id": config('FIREBASE_PRIVATE_KEY_ID', default=None),
                "private_key": private_key,
                "client_email": client_email,
                "client_id": config('FIREBASE_CLIENT_ID', default=None),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{client_email}"
            })
            firebase_admin.initialize_app(cred)
            _firebase_initialized = True
            return
        
        # Si no hay credenciales, no inicializar Firebase
        # Solo mostrar advertencia si estamos en modo DEBUG
        if settings.DEBUG:
            print("ADVERTENCIA: No se encontraron credenciales de Firebase. Las funciones de Firebase no estaran disponibles.")
            print("   Para habilitar Firebase, descarga el archivo de credenciales desde Firebase Console")
            print("   y guardalo como 'firebase-credentials.json' en la raiz del proyecto.")
            print("   O configura las variables de entorno FIREBASE_PROJECT_ID, FIREBASE_PRIVATE_KEY, FIREBASE_CLIENT_EMAIL")
        
    except Exception as e:
        # Solo mostrar error si estamos en modo DEBUG
        if settings.DEBUG:
            print(f"ERROR: Error al inicializar Firebase: {e}")
            print("   Las funciones de Firebase no estaran disponibles.")


def create_firebase_user(email, password, display_name=None, disabled=False):
    """
    Crea un usuario en Firebase Authentication.
    
    Args:
        email: Email del usuario
        password: Contraseña del usuario
        display_name: Nombre para mostrar (opcional)
        disabled: Si el usuario está deshabilitado (opcional)
    
    Returns:
        UserRecord: Objeto del usuario creado en Firebase, o None si hay error
    """
    try:
        initialize_firebase()
        
        if not _firebase_initialized:
            return None
        
        user_record = auth.create_user(
            email=email,
            password=password,
            display_name=display_name,
            disabled=disabled
        )
        
        return user_record
    except auth.EmailAlreadyExistsError:
        if settings.DEBUG:
            print(f"ADVERTENCIA: El usuario con email {email} ya existe en Firebase")
        # Intentar obtener el usuario existente
        return get_firebase_user_by_email(email)
    except Exception as e:
        if settings.DEBUG:
            print(f"ERROR: Error al crear usuario en Firebase: {e}")
        return None


def update_firebase_user(uid, email=None, password=None, display_name=None, disabled=None):
    """
    Actualiza un usuario en Firebase Authentication.
    
    Args:
        uid: UID del usuario en Firebase
        email: Nuevo email (opcional)
        password: Nueva contraseña (opcional)
        display_name: Nuevo nombre para mostrar (opcional)
        disabled: Si el usuario está deshabilitado (opcional)
    
    Returns:
        UserRecord: Objeto del usuario actualizado en Firebase, o None si hay error
    """
    try:
        initialize_firebase()
        
        if not _firebase_initialized:
            return None
        
        update_data = {}
        if email is not None:
            update_data['email'] = email
        if password is not None:
            update_data['password'] = password
        if display_name is not None:
            update_data['display_name'] = display_name
        if disabled is not None:
            update_data['disabled'] = disabled
        
        if update_data:
            user_record = auth.update_user(uid, **update_data)
            return user_record
        return None
    except Exception as e:
        if settings.DEBUG:
            print(f"ERROR: Error al actualizar usuario en Firebase: {e}")
        return None


def delete_firebase_user(uid):
    """
    Elimina un usuario de Firebase Authentication.
    
    Args:
        uid: UID del usuario en Firebase
    
    Returns:
        bool: True si se eliminó correctamente, False si hay error
    """
    try:
        initialize_firebase()
        
        if not _firebase_initialized:
            return False
        
        auth.delete_user(uid)
        return True
    except Exception as e:
        if settings.DEBUG:
            print(f"ERROR: Error al eliminar usuario de Firebase: {e}")
        return False


def get_firebase_user_by_email(email):
    """
    Obtiene un usuario de Firebase Authentication por email.
    Normaliza el email (trim y lowercase) antes de buscar.
    
    Args:
        email: Email del usuario
    
    Returns:
        UserRecord: Objeto del usuario en Firebase, o None si no existe o hay error
    """
    try:
        initialize_firebase()
        
        if not _firebase_initialized:
            return None
        
        # Normalizar el email antes de buscar
        if email:
            email = email.strip().lower()
        
        if not email:
            return None
        
        user_record = auth.get_user_by_email(email)
        return user_record
    except auth.UserNotFoundError:
        return None
    except Exception as e:
        if settings.DEBUG:
            print(f"ERROR: Error al obtener usuario de Firebase: {e}")
        return None


def sync_django_user_to_firebase(django_user, password=None, old_email=None):
    """
    Sincroniza un usuario de Django con Firebase Authentication.
    Busca el usuario por email actual o email anterior si se proporciona.
    
    Args:
        django_user: Instancia de User de Django
        password: Contraseña del usuario (opcional, si no se proporciona no se actualizará)
        old_email: Email anterior del usuario (opcional, útil cuando se cambia el email)
    
    Returns:
        UserRecord: Objeto del usuario en Firebase, o None si hay error o Firebase no está configurado
    """
    try:
        initialize_firebase()
        
        # Si Firebase no está inicializado, retornar None silenciosamente
        if not _firebase_initialized:
            return None
        
        if not django_user.email:
            if settings.DEBUG:
                print(f"ADVERTENCIA: No se puede sincronizar usuario en Firebase sin email: {django_user.username}")
            return None
        
        # Normalizar emails
        current_email = django_user.email.strip().lower() if django_user.email else None
        old_email_normalized = old_email.strip().lower() if old_email else None
        
        # Construir nombre para mostrar
        display_name = django_user.get_full_name() or django_user.username
        
        # Estrategia de búsqueda: buscar por email actual primero, luego por email anterior si se proporcionó
        firebase_user = None
        
        # 1. Buscar por email actual
        if current_email:
            firebase_user = get_firebase_user_by_email(current_email)
        
        # 2. Si no se encuentra y hay email anterior, buscar por email anterior
        if not firebase_user and old_email_normalized and old_email_normalized != current_email:
            firebase_user = get_firebase_user_by_email(old_email_normalized)
        
        if firebase_user:
            # Usuario existe en Firebase, actualizar
            update_data = {
                'display_name': display_name,
                'disabled': not django_user.is_active
            }
            
            # Si el email cambió, actualizarlo
            if current_email and firebase_user.email and firebase_user.email.strip().lower() != current_email:
                update_data['email'] = current_email
            
            # Si se proporciona contraseña, actualizarla
            if password:
                update_data['password'] = password
            
            try:
                return update_firebase_user(firebase_user.uid, **update_data)
            except Exception as e:
                error_msg = str(e)
                # Si el error es que el email ya está en uso, no actualizar el email
                if 'EMAIL_EXISTS' in error_msg or 'email already exists' in error_msg.lower():
                    if settings.DEBUG:
                        print(f"ADVERTENCIA: El email {current_email} ya está en uso. Actualizando solo otros campos.")
                    # Actualizar solo los campos que no son el email
                    update_data_no_email = {
                        'display_name': display_name,
                        'disabled': not django_user.is_active
                    }
                    if password:
                        update_data_no_email['password'] = password
                    return update_firebase_user(firebase_user.uid, **update_data_no_email)
                else:
                    raise
        else:
            # Usuario no existe en Firebase, crear nuevo
            # Si no hay contraseña, usar una contraseña temporal (el usuario puede cambiarla después)
            if not password:
                # Generar una contraseña temporal aleatoria o usar una por defecto
                # El usuario deberá usar "Olvidé mi contraseña" para establecer una contraseña real
                password = 'TempPass123!'  # Contraseña temporal segura
            
            try:
                firebase_user = create_firebase_user(
                    email=current_email,
                    password=password,
                    display_name=display_name,
                    disabled=not django_user.is_active
                )
                return firebase_user
            except Exception as e:
                error_msg = str(e)
                # Si el email ya existe, intentar obtenerlo y sincronizar
                if 'EMAIL_EXISTS' in error_msg or 'email already exists' in error_msg.lower():
                    firebase_user = get_firebase_user_by_email(current_email)
                    if firebase_user:
                        # Sincronizar con el usuario existente
                        update_data = {
                            'display_name': display_name,
                            'disabled': not django_user.is_active
                        }
                        if password:
                            update_data['password'] = password
                        return update_firebase_user(firebase_user.uid, **update_data)
                    else:
                        if settings.DEBUG:
                            print(f"ERROR: El email {current_email} ya existe pero no se pudo obtener el usuario")
                        return None
                else:
                    if settings.DEBUG:
                        print(f"ERROR: Error al crear usuario en Firebase: {error_msg}")
                    return None
    except Exception as e:
        if settings.DEBUG:
            print(f"ERROR: Error al sincronizar usuario con Firebase: {e}")
            import traceback
            traceback.print_exc()
        return None


def verify_firebase_password(email, password):
    """
    Verifica las credenciales de un usuario en Firebase Authentication usando la API REST.
    
    Args:
        email: Email del usuario
        password: Contraseña a verificar
    
    Returns:
        dict: Diccionario con 'success' (bool) y 'uid' (str) o 'error' (str)
    """
    try:
        initialize_firebase()
        
        if not _firebase_initialized:
            return {'success': False, 'error': 'Firebase no está inicializado'}
        
        # Normalizar el email (trim y lowercase) antes de enviarlo a Firebase
        email = email.strip().lower() if email else None
        
        if not email:
            return {'success': False, 'error': 'Email no válido'}
        
        # Obtener la API key de Firebase desde la configuración
        # La API key se puede obtener de las credenciales o configurarla como variable de entorno
        api_key = config('FIREBASE_WEB_API_KEY', default='AIzaSyBBaZY2-tp24fMt3uc13gLRpu9KnGOFA9g')
        
        # Endpoint de Firebase para verificar contraseña
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
        
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        if settings.DEBUG:
            print(f"DEBUG: Intentando autenticar en Firebase con email: {email}")
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if settings.DEBUG:
                print(f"DEBUG: Autenticación exitosa en Firebase para {email}")
            return {
                'success': True,
                'uid': data.get('localId'),
                'email': data.get('email')
            }
        else:
            try:
                error_data = response.json()
                error_message = error_data.get('error', {}).get('message', 'Error desconocido')
                error_code = error_data.get('error', {}).get('code', None)
                
                if settings.DEBUG:
                    print(f"DEBUG: Error en Firebase API: {error_code} - {error_message}")
                
                return {
                    'success': False,
                    'error': error_message,
                    'error_code': error_code
                }
            except:
                # Si no se puede parsear el JSON de error
                error_message = f"HTTP {response.status_code}: {response.text}"
                if settings.DEBUG:
                    print(f"DEBUG: Error no parseable en Firebase: {error_message}")
                return {
                    'success': False,
                    'error': error_message
                }
            
    except requests.exceptions.Timeout:
        error_msg = "Timeout al conectar con Firebase"
        if settings.DEBUG:
            print(f"ERROR: {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }
    except requests.exceptions.RequestException as e:
        error_msg = f"Error de conexión con Firebase: {str(e)}"
        if settings.DEBUG:
            print(f"ERROR: {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }
    except Exception as e:
        error_msg = f"Error inesperado: {str(e)}"
        if settings.DEBUG:
            print(f"ERROR: {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }

