"""
Django settings for crud project.
"""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load variables from .env in project root.
load_dotenv(BASE_DIR / '.env')


def _get_env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


def _get_env_list(name: str, default: list[str] | None = None) -> list[str]:
    value = os.getenv(name, '')
    if not value:
        return default or []
    return [item.strip() for item in value.split(',') if item.strip()]


# Deployment mode: development or production.
DJANGO_ENV = os.getenv('DJANGO_ENV', 'development').strip().lower()
IS_PRODUCTION = DJANGO_ENV == 'production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = _get_env_bool('DJANGO_DEBUG', default=not IS_PRODUCTION)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    if DEBUG or not IS_PRODUCTION:
        SECRET_KEY = 'dev-only-insecure-secret-key-change-me'
    else:
        raise ImproperlyConfigured('DJANGO_SECRET_KEY must be set in production.')

ALLOWED_HOSTS = _get_env_list('DJANGO_ALLOWED_HOSTS', default=['127.0.0.1', 'localhost'])
CSRF_TRUSTED_ORIGINS = _get_env_list('DJANGO_CSRF_TRUSTED_ORIGINS', default=[])

if IS_PRODUCTION and not ALLOWED_HOSTS:
    raise ImproperlyConfigured('DJANGO_ALLOWED_HOSTS must be set in production.')


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'notes',
    'registration',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'crud.middleware.request_timing_middleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'crud.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'crud.wsgi.application'


# Database
# Supports sqlite by default and postgres via env credentials.
DB_ENGINE = os.getenv('DB_ENGINE', 'sqlite3').strip().lower()

if DB_ENGINE in {'postgresql', 'postgres', 'django.db.backends.postgresql'}:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', ''),
            'USER': os.getenv('DB_USER', ''),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', '127.0.0.1'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.getenv('DB_NAME', str(BASE_DIR / 'db.sqlite3')),
        }
    }


# Password validation
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


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'notes' / 'static',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Hardened defaults when running in production.
if IS_PRODUCTION:
    SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '31536000'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = _get_env_bool('SECURE_SSL_REDIRECT', default=True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'
