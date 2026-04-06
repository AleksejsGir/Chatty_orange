#!/bin/sh

# Выход при ошибке
set -e

# Ожидание готовности базы данных
echo "Waiting for database..."
sleep 10
echo "Database is ready!"

# Применение миграций
echo "Applying migrations..."
python manage.py migrate --noinput

# Сбор статических файлов (новая секция)
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Запуск Gunicorn
echo "Starting Gunicorn..."
exec gunicorn Chatty_orange.wsgi:application $GUNICORN_CMD_ARGS