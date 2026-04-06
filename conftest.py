import os
import sys
import pytest
import django
from pathlib import Path

# Определяем корневую директорию проекта
ROOT_DIR = Path(__file__).resolve().parent

# Добавляем корневую директорию в Python path
sys.path.insert(0, str(ROOT_DIR))

# Устанавливаем переменную окружения для Django настроек
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Chatty_orange.settings.development')

# Важно! Настраиваем Django ДО любых импортов моделей
django.setup()

# Добавляем маркер для использования БД
pytest_plugins = ['pytest_django']