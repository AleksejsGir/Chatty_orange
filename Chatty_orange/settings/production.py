"""
Production settings for Chatty_orange project.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', 'False').lower() in ('true', '1', 't')

# ✅ ИСПРАВЛЕНО: Правильная обработка ALLOWED_HOSTS
allowed_hosts_str = os.getenv('DJANGO_ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_str.split(',') if host.strip()] if allowed_hosts_str else []

# ✅ ИСПРАВЛЕНО: Правильная обработка CSRF_TRUSTED_ORIGINS
csrf_origins_str = os.getenv('CSRF_TRUSTED_ORIGINS', '')
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in csrf_origins_str.split(',') if origin.strip()] if csrf_origins_str else []

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# ========== СТАТИЧЕСКИЕ ФАЙЛЫ (КРИТИЧЕСКИ ВАЖНО!) ==========
# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Directories where Django will search for static files
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# WhiteNoise для обслуживания статических файлов в продакшене
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Дополнительные настройки для статических файлов
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# WhiteNoise настройки для лучшей производительности
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True
WHITENOISE_SKIP_COMPRESS_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'zip', 'gz', 'tgz', 'bz2', 'tbz', 'xz', 'br']

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Database
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.getenv('DB_NAME', 'chatty_db_prod'),
        'USER': os.getenv('DB_USER', 'chatty_user_prod'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'db_prod'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Email SMTP settings for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() in ('true', '1', 't')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', f'Chatty <{EMAIL_HOST_USER}>')

# Отключаем Debug Toolbar в продакшене
if 'debug_toolbar' in INSTALLED_APPS:
    INSTALLED_APPS.remove('debug_toolbar')

# Удаляем debug_toolbar middleware в продакшене
MIDDLEWARE = [middleware for middleware in MIDDLEWARE if 'debug_toolbar' not in middleware]

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/django-error.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.staticfiles': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Ensure log directory exists
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# ========== ДОПОЛНИТЕЛЬНЫЕ НАСТРОЙКИ ДЛЯ ОТЛАДКИ ==========
# Выводим информацию о настройках в лог для диагностики
import logging
logger = logging.getLogger(__name__)
logger.info(f"ALLOWED_HOSTS: {ALLOWED_HOSTS}")
logger.info(f"CSRF_TRUSTED_ORIGINS: {CSRF_TRUSTED_ORIGINS}")
logger.info(f"STATIC_ROOT: {STATIC_ROOT}")
logger.info(f"STATICFILES_DIRS: {STATICFILES_DIRS}")
logger.info(f"DEBUG: {DEBUG}")