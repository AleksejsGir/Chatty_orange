#!/bin/sh
 set -e

 # Ожидаем доступности БД
 /app/wait-for-db.sh db 5432

 # Выполняем миграции
 python manage.py migrate

# # Создаем суперпользователя, если его нет
# python /app/create_admin.py

 # Запускаем Django (используя Gunicorn или runserver)
 exec gunicorn Chatty_orange.wsgi:application --bind 0.0.0.0:8000
 # или просто:
 # exec python manage.py runserver 0.0.0.0:8000