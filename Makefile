# Makefile
.PHONY: test test-coverage test-verbose test-failed

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