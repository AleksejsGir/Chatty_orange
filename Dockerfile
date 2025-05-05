# Используем официальный образ Python нужной версии
FROM python:3.11-slim

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1  # Предотвращает создание .pyc файлов
ENV PYTHONUNBUFFERED 1       # Вывод Python будет сразу отправляться в терминал (логи Docker)

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Устанавливаем системные зависимости, если они нужны (например, для psycopg2)
# psycopg2-binary обычно их не требует, но оставим как пример
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     libpq-dev \
#     && rm -rf /var/lib/apt/lists/*

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копируем весь код проекта в рабочую директорию
COPY . .

# Открываем порт 8000, на котором будет работать Django development server
EXPOSE 8000

# Команда по умолчанию для запуска контейнера
# Запускаем Django development server, доступный извне контейнера (на 0.0.0.0)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# <!-- TODO: При переходе на production использовать gunicorn или uwsgi вместо runserver. -->
# <!-- TODO: Рассмотреть многостадийную сборку для уменьшения размера финального образа. -->
# <!-- TODO: Добавить команду для сбора статики (collectstatic) при сборке production-образа. -->


#!/bin/sh
python manage.py migrate
exec "$@"
