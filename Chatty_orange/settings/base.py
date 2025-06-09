"""
Base settings for Chatty_orange project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Загружаем переменные окружения из .env файла
load_dotenv(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'default-insecure-secret-key-for-dev')

# Application definition
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # --- Наши приложения ---
    'users.apps.UsersConfig',
    'posts.apps.PostsConfig',
    'subscriptions.apps.SubscriptionsConfig',
    'orange_assistant.apps.OrangeAssistantConfig',
    # --- Сторонние приложения ---
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'debug_toolbar',
    'django_bootstrap5',
    'ckeditor',  # Добавляем CKEditor
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'Chatty_orange.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'Chatty_orange.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Berlin'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'users.CustomUser'

# Authentication Settings
LOGIN_URL = 'account_login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Django Debug Toolbar Settings
INTERNAL_IPS = ['127.0.0.1']

# Django Allauth Settings
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
SITE_ID = 1
ACCOUNT_LOGIN_METHODS = {'email', 'username'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_LOGOUT_ON_GET = False
ACCOUNT_EMAIL_SUBJECT_PREFIX = '[Chatty] '

ACCOUNT_AUTHENTICATION_METHOD = 'email'  # Использовать email для входа
ACCOUNT_USERNAME_REQUIRED = False  # Не требовать username при регистрации через Google
ACCOUNT_UNIQUE_EMAIL = True  # Email должен быть уникальным
# SOCIALACCOUNT_LOGIN_ON_GET = False  # Требовать POST для безопасности

# Для лучшего UX
ACCOUNT_SESSION_REMEMBER = True  # Опция "Запомнить меня"
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True  # Автологин после подтверждения

ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = '/'
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = '/'

# Автоматически подтягивать email и имя из Google
SOCIALACCOUNT_AUTO_SIGNUP = False #Это предотвратит автоматическое создание пользователя allauth.
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'  # Google уже проверил email
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_STORE_TOKENS = True
# Для автоматической связки аккаунтов с одинаковым email:
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True

# Адаптер для обработки конфликтов email
SOCIALACCOUNT_ADAPTER = 'users.adapters.MySocialAccountAdapter'

# Google OAuth Settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
        # Добавьте маппинг полей:
        'FIELDS': [
            'email',
            'first_name',
            'last_name',
        ],
    }
}



     #CKEditor
CKEDITOR_JQUERY_URL = 'https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js'
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_BASEPATH = "/static/ckeditor/ckeditor/"
CKEDITOR_RESTRICT_BY_USER = True
CKEDITOR_FORCE_JPEG_COMPRESSION = True
CKEDITOR_FILENAME_GENERATOR = 'utils.get_filename'

# Указываем использовать последнюю версию CKEditor
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript'],
            ['TextColor', 'BGColor'],
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent'],
            ['Link', 'Unlink'],
            ['RemoveFormat', 'Source'],
            ['Styles', 'Format', 'Font', 'FontSize'],
            ['Image', 'Table'],
            ['Maximize']
        ],
        'width': '100%',
        'height': 300,
        'removePlugins': 'stylesheetparser',
        'allowedContent': True,
    },
}
JAZZMIN_SETTINGS = {
    "site_title": "Chatty orange",  # Заголовок административной панели
    "site_header": "Chatty orange: Admin",  # Заголовок окна браузера
    "site_brand": "Chatty orange",  # Бренд сайта
    "welcome_sign": "Welcome to Chatty orange: Admin",  # Приветственное сообщение
    "copyright": "Chatty orange GmbH",  # Информация о копирайте
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        # {"name": "Catalog", "url": "news:catalog", "new_window": True},
        {"name": "Support", "url": "https://google.com", "new_window": True},
    ],
    "usermenu_links": [
        {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},
        {"model": "auth.user"}
    ],
    "show_sidebar": True,  # Показать боковую панель
    "navigation_expanded": True,  # Развернуть навигацию
    "hide_apps": [],  # Скрыть приложения
    "hide_models": [],  # Скрыть модели
    "default_icon_parents": "fas fa-chevron-circle-right",  # Иконка для родительских элементов
    "default_icon_children": "fas fa-circle",  # Иконка для дочерних элементов
    "related_modal_active": False,  # Включить модальные окна для связанных объектов
    "custom_css": None,  # Пользовательский CSS
    "custom_js": None,  # Пользовательский JS
    "use_google_fonts_cdn": True,  # Использовать Google Fonts CDN
    "show_ui_builder": False,  # Показать конструктор интерфейса
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": True,
    "brand_small_text": False,
    "brand_colour": "navbar-secondary",
    "accent": "accent-pink",
    "navbar": "navbar-danger navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-light-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": True,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": True,
    "theme": "cyborg",
    "dark_mode_theme": "cyborg",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}