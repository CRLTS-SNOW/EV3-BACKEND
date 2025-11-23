import os
from pathlib import Path
from decouple import config, Csv
from dj_database_url import parse as db_url

BASE_DIR = Path(__file__).resolve().parent.parent

# Buscar .env en el directorio raíz del proyecto
ENV_FILE = BASE_DIR / '.env'

SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production-key-12345')

DEBUG = config('DEBUG', default=True, cast=bool)

# Añadí tu host local aquí por seguridad
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '98.95.67.251', 'ec2-98-95-67-251.compute-1.amazonaws.com']


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    
    # REST Framework
    'rest_framework',
    'corsheaders',
    
    # Tu app
    'gestion',
]

# Pillow para manejo de imágenes
try:
    import PIL
except ImportError:
    pass

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS debe estar antes de CommonMiddleware
    'django.middleware.common.CommonMiddleware',
    'gestion.middleware.DisableCSRFForAPI',  # Deshabilitar CSRF para APIs REST
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


DATABASES = {
    'default': config(
        'DATABASE_URL',
        default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'),
        cast=db_url
    )
}


# Backend de autenticación personalizado que permite login con email o username
# SOLO Firebase - Django NO se usa para autenticación
AUTHENTICATION_BACKENDS = [
    'gestion.backends.EmailOrUsernameBackend',  # Backend personalizado (SOLO Firebase)
    # 'django.contrib.auth.backends.ModelBackend',  # DESHABILITADO - Solo Firebase
]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# URL a la que Django redirige si un usuario NO está logueado
LOGIN_URL = 'login'

# URL a la que Django redirige DESPUÉS de un login exitoso
LOGIN_REDIRECT_URL = 'product_list' # El 'name' de tu lista de productos

# URL a la que Django redirige DESPUÉS de un logout
LOGOUT_REDIRECT_URL = 'login' # Lo enviamos de vuelta al login

# CORS Configuration para React
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://98.95.67.251",
    "http://ec2-98-95-67-251.compute-1.amazonaws.com",
]

CORS_ALLOW_CREDENTIALS = True

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://98.95.67.251",
    "http://ec2-98-95-67-251.compute-1.amazonaws.com",
]

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'gestion.pagination.OptimizedPageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    # Optimizaciones de rendimiento
    'DEFAULT_THROTTLE_CLASSES': [],
    'DEFAULT_THROTTLE_RATES': {},
}
