#!/bin/sh

# Выход при ошибке
set -e

# Установка необходимых пакетов
apt-get update && apt-get install -y netcat-openbsd

# Ожидание готовности базы данных
echo "Waiting for database..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "Database is ready!"

echo "Entrypoint: Applying database migrations..."
python manage.py migrate --noinput

echo "Entrypoint: Starting Gunicorn..."
# Запускаем Gunicorn
# Используем переменную окружения GUNICORN_CMD_ARGS
exec gunicorn Chatty_orange.wsgi:application $GUNICORN_CMD_ARGS