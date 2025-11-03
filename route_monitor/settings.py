from pathlib import Path
from datetime import timedelta
import os
import dj_database_url
from corsheaders.defaults import default_headers

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY', 'y$1lk3vhs23xh&9@#ar1h*l=1f7v4afl^7&8iizz7kd4vdutxp')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = os.environ.get(
    'ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'routes',
    'rest_framework_simplejwt',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    # Must be right after SecurityMiddleware
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS settings - Open for Capacitor.js frontend
# Open for Capacitor.js which doesn't have a specific domain
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = [
    # Capacitor.js origins
    "capacitor://localhost",
    "http://localhost",
    "https://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    # Web origins (if any)
    'https://route-monitor-frontend-sandy.vercel.app',
    'https://rm-frontend-three.vercel.app',
    'https://admin.routemonitor.app',
    'https://www.admin.routemonitor.app',
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = list(default_headers) + [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# CSRF settings - Open for Capacitor.js frontend
CSRF_TRUSTED_ORIGINS = [
    # Capacitor.js origins
    "capacitor://localhost",
    "http://localhost",
    "https://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # Web origins (if any)
    'https://route-monitor-frontend-sandy.vercel.app',
    'https://rm-frontend-three.vercel.app',
    'https://admin.routemonitor.app',
    'https://www.admin.routemonitor.app',
]

if DEBUG:
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SAMESITE = 'Lax'
else:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SAMESITE = 'None'

ROOT_URLCONF = 'route_monitor.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'route_monitor.wsgi.application'

# Database
# Use DATABASE_URL if available (production PostgreSQL), otherwise fallback to SQLite for local development
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Check if SSL is required via environment variable
    # Default to False for internal Docker/Coolify connections
    ssl_require_env = os.environ.get(
        'POSTGRES_SSL_REQUIRE', 'false').lower() == 'true'
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=ssl_require_env
        )
    }
else:
    # Fallback to SQLite for local development only
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
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

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Internationalization
LANGUAGE_CODE = 'es-pe'  # Spanish (Peru)
TIME_ZONE = 'America/Lima'  # Peru's time zone
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# WhiteNoise configuration for serving static files in production
# WhiteNoise serves files from STATIC_ROOT when DEBUG=False
# Don't set STATICFILES_STORAGE in production - let WhiteNoise handle it
# STATICFILES_STORAGE is only used during collectstatic
if not DEBUG:
    # For production: use WhiteNoise storage during collectstatic
    STATICFILES_STORAGE = 'whitenoise.storage.WhiteNoiseStaticFilesStorage'
    # WhiteNoise settings
    WHITENOISE_USE_FINDERS = False  # Only serve from STATIC_ROOT, not from finders
    WHITENOISE_AUTOREFRESH = False  # Don't check for file changes in production
    WHITENOISE_MANIFEST_STRICT = False  # Don't fail if manifest issues
else:
    # In development, use default storage
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Only enable these in production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
else:
    SECURE_SSL_REDIRECT = False
