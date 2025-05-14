#!/bin/sh

# Выход при ошибке
set -e

echo "Entrypoint: Applying database migrations..."
# Активируем виртуальное окружение (если оно используется в Dockerfile.prod)
# Если venv в /opt/venv, как мы делали в Dockerfile.prod:
. /opt/venv/bin/activate
python manage.py migrate --noinput

# Команда collectstatic уже выполнена при сборке образа в Dockerfile.prod,
# но если вы хотите собирать статику при каждом запуске контейнера (не рекомендуется для production),
# можно раскомментировать следующую строку:
# echo "Entrypoint: Collecting static files..."
# python manage.py collectstatic --noinput --clear

echo "Entrypoint: Starting Gunicorn..."
# Запускаем Gunicorn
# Переменная окружения GUNICORN_CMD_ARGS должна быть установлена в docker-compose.prod.yml или .env.prod
# Например: GUNICORN_CMD_ARGS="--workers 3 --bind 0.0.0.0:8000"
# Chatty_orange.wsgi:application - это ваше WSGI приложение
exec gunicorn Chatty_orange.wsgi:application $GUNICORN_CMD_ARGS

# <!-- TODO: Добавить wait-for-it.sh или аналогичный скрипт для ожидания готовности базы данных перед запуском миграций. -->
# <!-- TODO: Переменная GUNICORN_CMD_ARGS должна быть определена в .env.prod или docker-compose.prod.yml. -->