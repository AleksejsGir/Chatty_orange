# Makefile для проекта Chatty Orange
.PHONY: test test-coverage test-verbose test-failed test-ai test-ai-coverage test-ai-integration

# ===== ОСНОВНЫЕ КОМАНДЫ ТЕСТИРОВАНИЯ =====

# Запуск всех тестов
test:
	docker-compose exec web pytest

# Запуск тестов с отчетом о покрытии
test-coverage:
	docker-compose exec web pytest --cov=. --cov-report=html --cov-report=term

# Запуск тестов с подробным выводом
test-verbose:
	docker-compose exec web pytest -vv

# Запуск только провалившихся тестов
test-failed:
	docker-compose exec web pytest --lf

# Запуск конкретного файла тестов
test-file:
	docker-compose exec web pytest $(FILE)

# Запуск тестов конкретного приложения
test-app:
	docker-compose exec web pytest tests/test_$(APP)/

# ===== КОМАНДЫ ДЛЯ ORANGE ASSISTANT =====

# Запуск всех тестов Orange Assistant
test-ai:
	@echo "🤖 Запуск тестов Orange Assistant..."
	docker-compose exec web pytest tests/test_orange_assistant/ -v

# Покрытие только Orange Assistant
test-ai-coverage:
	@echo "📊 Проверка покрытия Orange Assistant..."
	docker-compose exec web pytest tests/test_orange_assistant/ --cov=orange_assistant --cov-report=term-missing --cov-report=html

# Интеграционные тесты ИИ
test-ai-integration:
	@echo "🔗 Интеграционные тесты Orange Assistant..."
	docker-compose exec web pytest tests/test_orange_assistant/test_integration.py -v

# Тесты AI сервисов (основной компонент)
test-ai-services:
	@echo "🧠 Тестирование AI сервисов..."
	docker-compose exec web pytest tests/test_orange_assistant/test_ai_services.py -v

# Тесты представлений ИИ
test-ai-views:
	@echo "🌐 Тестирование AI представлений..."
	docker-compose exec web pytest tests/test_orange_assistant/test_views.py -v

# Быстрая проверка ИИ без подробностей
test-ai-quick:
	@echo "⚡ Быстрая проверка Orange Assistant..."
	docker-compose exec web pytest tests/test_orange_assistant/ -q

# ===== КОМАНДЫ ДЛЯ ОТДЕЛЬНЫХ МОДУЛЕЙ =====

# Тесты постов
test-posts:
	docker-compose exec web pytest tests/test_models/test_post_models.py tests/test_views/test_post_views.py tests/test_forms/test_post_forms.py -v

# Тесты пользователей
test-users:
	docker-compose exec web pytest tests/test_models/test_user_models.py tests/test_views/test_user_views.py tests/test_forms/test_user_forms.py -v

# Тесты подписок
test-subscriptions:
	docker-compose exec web pytest tests/test_models/test_subscription_models.py tests/test_views/test_subscription_views.py -v

# ===== ПОЛНОЕ ТЕСТИРОВАНИЕ =====

# Полное тестирование всего проекта с покрытием
test-full:
	@echo "🚀 Полное тестирование проекта..."
	docker-compose exec web pytest --cov=. --cov-report=html --cov-report=term --cov-report=xml -v

# Тестирование для CI/CD
test-ci:
	@echo "🤖 CI/CD тестирование..."
	docker-compose exec web pytest --cov=. --cov-report=xml --tb=short

# Проверка качества кода и тестирование
test-quality:
	@echo "✨ Проверка качества кода..."
	docker-compose exec web flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	docker-compose exec web pytest --cov=. --cov-report=term-missing

# ===== ВСПОМОГАТЕЛЬНЫЕ КОМАНДЫ =====

# Очистка кеша pytest
test-clean:
	docker-compose exec web find . -name "*.pyc" -delete
	docker-compose exec web find . -name "__pycache__" -type d -exec rm -rf {} +
	docker-compose exec web rm -rf .pytest_cache/

# Показать статистику тестов
test-stats:
	@echo "📈 Статистика тестов..."
	docker-compose exec web pytest --collect-only -q | grep "test session starts" -A 100

# Помощь по командам тестирования
test-help:
	@echo "🔧 Доступные команды тестирования:"
	@echo ""
	@echo "Основные команды:"
	@echo "  make test              - Запуск всех тестов"
	@echo "  make test-coverage     - Тесты с покрытием"
	@echo "  make test-verbose      - Подробный вывод"
	@echo "  make test-failed       - Только упавшие тесты"
	@echo ""
	@echo "Orange Assistant:"
	@echo "  make test-ai           - Все тесты ИИ"
	@echo "  make test-ai-coverage  - Покрытие ИИ"
	@echo "  make test-ai-integration - Интеграционные тесты ИИ"
	@echo "  make test-ai-services  - Тесты AI сервисов"
	@echo "  make test-ai-views     - Тесты AI представлений"
	@echo "  make test-ai-quick     - Быстрая проверка ИИ"
	@echo ""
	@echo "По модулям:"
	@echo "  make test-posts        - Тесты постов"
	@echo "  make test-users        - Тесты пользователей"
	@echo "  make test-subscriptions - Тесты подписок"
	@echo ""
	@echo "Полное тестирование:"
	@echo "  make test-full         - Все тесты с покрытием"
	@echo "  make test-ci           - Тесты для CI/CD"
	@echo "  make test-quality      - Проверка качества"
	@echo ""
	@echo "Вспомогательные:"
	@echo "  make test-clean        - Очистка кеша"
	@echo "  make test-stats        - Статистика тестов"
	@echo "  make test-help         - Эта справка"

# ===== КОМАНДЫ ДЛЯ РАЗРАБОТКИ =====

# Установка зависимостей
install:
	docker-compose exec web pip install -r requirements.txt

# Применение миграций
migrate:
	docker-compose exec web python manage.py migrate

# Создание миграций
makemigrations:
	docker-compose exec web python manage.py makemigrations

# Сбор статических файлов
collectstatic:
	docker-compose exec web python manage.py collectstatic --noinput

# Создание суперпользователя
createsuperuser:
	docker-compose exec web python manage.py createsuperuser

# Запуск Django shell
shell:
	docker-compose exec web python manage.py shell

# Просмотр логов
logs:
	docker-compose logs -f

# Перезапуск сервисов
restart:
	docker-compose restart

# Полная пересборка
rebuild:
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d