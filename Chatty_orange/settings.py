"""
Django settings for Chatty_orange project.
... (остальная документация) ...
"""
import os # Добавлено
from pathlib import Path
from dotenv import load_dotenv # Добавлено

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Загружаем переменные окружения из .env файла
load_dotenv(BASE_DIR / '.env') # Добавлено

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Читаем SECRET_KEY из переменных окружения
SECRET_KEY = os.getenv('SECRET_KEY', 'default-insecure-secret-key-for-dev') # Изменено

# SECURITY WARNING: don't run with debug turned on in production!
# Читаем DEBUG из переменных окружения, преобразуем в Boolean
# По умолчанию False, если переменная не найдена
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't') # Изменено

# ALLOWED_HOSTS можно будет позже тоже вынести в .env
ALLOWED_HOSTS = []
# Если DEBUG=True, можно добавить стандартные хосты для разработки
if DEBUG:
    ALLOWED_HOSTS.extend(['localhost', '127.0.0.1'])


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin', # Добавлено для доступа к админке
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # --- Ваши приложения ---
    'users.apps.UsersConfig', # Добавляем приложение users
    # <!-- AI-TODO: Добавлять сюда новые приложения (posts, subscriptions) по мере их создания -->
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Chatty_orange.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Указываем Django искать шаблоны в папке templates в корне проекта
        'DIRS': [BASE_DIR / 'templates'], # Убедитесь, что эта строка есть
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug', # Добавлено для контекста DEBUG
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Chatty_orange.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# Настройки базы данных читаются из переменных окружения
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('DB_NAME', BASE_DIR / 'db.sqlite3'), # Имя БД или путь к файлу SQLite
        'USER': os.getenv('DB_USER', ''), # Имя пользователя БД
        'PASSWORD': os.getenv('DB_PASSWORD', ''), # Пароль БД
        'HOST': os.getenv('DB_HOST', 'localhost'), # Хост БД (имя сервиса в Docker)
        'PORT': os.getenv('DB_PORT', '5432'), # Порт БД
    }
}
# Если используем SQLite, нужно указать только ENGINE и NAME
if DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
     DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3', # Используем старый путь если не PostgreSQL
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

# Модель пользователя (будет добавлена в задаче №4)
# AUTH_USER_MODEL = 'users.CustomUser' # Пока закомментировано

# Internationalization

LANGUAGE_CODE = 'ru-ru' # Можно сменить на русский
TIME_ZONE = 'Europe/Berlin' # Можно сменить на ваш часовой пояс

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
# Указываем Django, где искать статичные файлы помимо папок static внутри приложений
STATICFILES_DIRS = [
    BASE_DIR / "static", # Добавлено для общих статических файлов проекта
]
# STATIC_ROOT = BASE_DIR / "staticfiles" # Понадобится для сбора статики на production

# Media files (User Uploads)
# MEDIA_URL = '/media/' # Понадобится для загрузки файлов
# MEDIA_ROOT = BASE_DIR / 'media' # Понадобится для загрузки файлов

# Default primary key field type
# ... (без изменений) ...
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email Backend for Password Reset (Задача №6)
# Используем вывод в консоль для отладки
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # Добавлено

# Login/Logout Redirects (будет использоваться в Задаче №5)
LOGIN_URL = 'login' # Имя URL-паттерна для страницы входа
LOGIN_REDIRECT_URL = '/' # Куда перенаправлять после успешного входа
LOGOUT_REDIRECT_URL = '/' # Куда перенаправлять после выхода

# <!-- TODO: Проверить и настроить AUTH_USER_MODEL после создания модели пользователя (Задача 4). -->
# <!-- TODO: Настроить STATIC_ROOT и MEDIA_ROOT/MEDIA_URL при необходимости. -->
# <!-- TODO: Рассмотреть возможность разделения настроек на base.py, dev.py, prod.py для более сложных конфигураций. -->
# <!-- TODO: Добавить 'django.contrib.admin' в INSTALLED_APPS, если еще не добавлено (добавил выше). -->
# <!-- TODO: Добавить 'users.apps.UsersConfig' в INSTALLED_APPS (добавил выше). -->