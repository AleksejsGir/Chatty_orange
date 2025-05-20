# 📘 Chatty Orange - Социальная сеть на Django

Chatty Orange — полноценная социальная сеть, разработанная на Django. В этой платформе пользователи могут регистрироваться, создавать посты, комментировать, лайкать публикации и подписываться на интересных авторов.

**Проект:** [https://chattyorange.eu](https://chattyorange.eu)

## 🎯 Функциональность

- **Аутентификация:**
  - Регистрация по email с подтверждением
  - Авторизация по email и паролю
  - Сброс пароля

- **Профиль пользователя:**
  - Просмотр и редактирование профиля
  - Загрузка аватара
  - Управление личной информацией (имя, описание, контакты)

- **Контент:**
  - Создание, редактирование и удаление постов
  - Прикрепление изображений к постам
  - Комментирование постов
  - Лайки постов
  - Теги для категоризации контента
  - Просмотр ленты всех постов и ленты подписок

- **Подписки:**
  - Подписка/отписка на других пользователей
  - Персонализированная лента постов от авторов, на которых вы подписаны
  - Просмотр списков подписчиков и подписок

- **Администрирование:**
  - Панель администратора для модерации контента
  - Управление пользователями, постами и комментариями
  - Аналитика активности пользователей

## 🛠️ Технологический стек

- **Язык программирования:** Python 3.11
- **Веб-фреймворк:** Django 5.1.5
- **Шаблоны:** Django Templates + Bootstrap 5 + CSS
- **Frontend:** JavaScript (для интерактивных элементов)
- **ORM:** Django ORM
- **База данных:** PostgreSQL 15
- **Хранение файлов:** локально/MinIO
- **Контейнеризация:** Docker + Docker Compose
- **Веб-сервер:** Nginx + Gunicorn
- **SSL:** Let's Encrypt
- **Тестирование:** Pytest / Unittest
- **Контроль версий:** Git + GitHub
- **CI/CD:** Docker Hub

## 📂 Структура проекта

Проект имеет модульную структуру и следует принципам Django-приложений:

```
chatty/
├── Chatty_orange/          # Основное приложение (настройки)
├── users/                  # Управление пользователями
├── posts/                  # Посты, комментарии, лайки
├── subscriptions/          # Подписки и лента
├── templates/              # Глобальные шаблоны
├── static/                 # Статические файлы
└── media/                  # Загружаемые файлы
```

Подробная информация о структуре проекта доступна в файле [Project_structure.md](Project_structure.md).

## 🚀 Установка и запуск

### Продакшен-развертывание

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/AleksejsGir/Chatty_orange.git
   cd Chatty_orange
   ```

2. Создайте файл `.env.prod` в корневой директории проекта:
   ```
   # Django Settings
   DJANGO_SETTINGS_MODULE=Chatty_orange.settings.production
   DJANGO_DEBUG=False
   SECRET_KEY=your_secure_secret_key
   
   # Domain and Host Settings
   DJANGO_ALLOWED_HOSTS=yourdomain.com www.yourdomain.com
   CSRF_TRUSTED_ORIGINS=https://yourdomain.com https://www.yourdomain.com
   
   # Database Settings
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=chatty_db
   DB_USER=db_user
   DB_PASSWORD=secure_password
   DB_HOST=db_prod
   DB_PORT=5432
   
   # Email Settings
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=your_app_password
   DEFAULT_FROM_EMAIL=Your Site <your_email@gmail.com>
   
   # Gunicorn Settings
   GUNICORN_CMD_ARGS=--workers 3 --bind 0.0.0.0:8000 --timeout 120
   ```

3. Запустите проект с использованием Docker Compose:
   ```bash
   docker compose -f docker-compose.prod.yml up -d
   ```

4. Выполните миграции и создайте суперпользователя:
   ```bash
   docker compose -f docker-compose.prod.yml exec web_prod python manage.py migrate
   docker compose -f docker-compose.prod.yml exec web_prod python manage.py createsuperuser
   ```

5. Приложение будет доступно по настроенному домену с SSL-сертификатом.

### Локальная разработка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/AleksejsGir/Chatty_orange.git
   cd Chatty_orange
   ```

2. Создайте файл `.env` в корневой директории проекта:
   ```
   # Django Settings
   DEBUG=True
   SECRET_KEY=dev_secret_key
   
   # Database Settings
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=chatty_db_dev
   DB_USER=chatty_user
   DB_PASSWORD=password
   DB_HOST=db
   DB_PORT=5432
   ```

3. Запустите проект с использованием Docker Compose для разработки:
   ```bash
   docker-compose up -d
   ```

4. Выполните миграции и создайте суперпользователя:
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```

5. Приложение будет доступно по адресу: http://localhost:8000

## 🧪 Тестирование

Для запуска тестов выполните:

```bash
# В продакшен-окружении
docker compose -f docker-compose.prod.yml exec web_prod python manage.py test

# В окружении разработки
docker-compose exec web python manage.py test
```

## 📊 Архитектура проекта

Проект реализован в монолитной архитектуре и состоит из следующих приложений:

- **Chatty_orange** - базовые настройки, разделенные на модули для разработки и продакшена
- **users** - управление пользователями, профили, аутентификация
- **posts** - модели и представления для постов, комментариев и лайков
- **subscriptions** - логика подписок и формирования персонализированной ленты

## 📚 Документация API и руководства

- [Структура проекта](Project_structure.md)
- [Руководство по развертыванию](deployment_guide.md)
- [Руководство пользователя](user_guide.md)

## 👨‍💻 Авторы

- Aleksejs Giruckis - [GitHub](https://github.com/AleksejsGir/Chatty_orange)
- Igor Pronin - [GitHub](https://github.com/AleksejsGir/Chatty_orange)
- Victor Yerokhov - [GitHub](https://github.com/AleksejsGir/Chatty_orange)
- Maxim Schneider - [GitHub](https://github.com/AleksejsGir/Chatty_orange)
- Ivan Miakinnov - [GitHub](https://github.com/AleksejsGir/Chatty_orange)



## 📄 Лицензия

[MIT](LICENSE)