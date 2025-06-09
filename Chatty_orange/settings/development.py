"""
Development settings for Chatty_orange project.
"""

from .base import *
from django.core.exceptions import ImproperlyConfigured

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Database
DB_ENGINE = os.getenv('DB_ENGINE')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

if not all([DB_ENGINE, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT]):
    raise ImproperlyConfigured(
        "Не все переменные окружения для подключения к базе данных установлены! "
        "Проверьте ваш .env файл и убедитесь, что DB_ENGINE, DB_NAME, DB_USER, "
        "DB_PASSWORD, DB_HOST, DB_PORT определены."
    )

DATABASES = {
    'default': {
        'ENGINE': DB_ENGINE,
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
    }
}

# Email Console Backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Debug Toolbar
INTERNAL_IPS = ['127.0.0.1']