# Makefile для FastAPI проекта с Clean Architecture

# Переменные
PYTHON = python3
VENV = venv
PIP = $(VENV)/bin/pip
PYTHON_VENV = $(VENV)/bin/python
UVICORN = $(VENV)/bin/uvicorn
ALEMBIC = $(VENV)/bin/alembic

# Настройки приложения
APP_MODULE = app.main:app
HOST = 0.0.0.0
PORT = 8000
WORKERS = 1

# Цвета для вывода
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

.PHONY: help install install-dev run run-dev test test-unit test-integration test-e2e clean migrate migrate-upgrade migrate-downgrade setup-db delete-user format lint check

# Основная команда помощи
help:
	@echo "$(GREEN)Доступные команды:$(NC)"
	@echo "  $(YELLOW)install$(NC)        - Установка зависимостей"
	@echo "  $(YELLOW)install-dev$(NC)     - Установка зависимостей для разработки"
	@echo "  $(YELLOW)run$(NC)            - Запуск приложения в production режиме"
	@echo "  $(YELLOW)run-dev$(NC)        - Запуск приложения в development режиме"
	@echo "  $(YELLOW)test$(NC)           - Запуск всех тестов"
	@echo "  $(YELLOW)test-unit$(NC)      - Запуск unit тестов"
	@echo "  $(YELLOW)test-integration$(NC) - Запуск integration тестов"
	@echo "  $(YELLOW)test-e2e$(NC)       - Запуск end-to-end тестов"
	@echo "  $(YELLOW)test-api-manual$(NC) - Ручное тестирование API"
	@echo "  $(YELLOW)test-imports$(NC)    - Тестирование импортов"
	@echo "  $(YELLOW)clean$(NC)          - Очистка кэша и временных файлов"
	@echo "  $(YELLOW)migrate$(NC)        - Создание новой миграции"
	@echo "  $(YELLOW)migrate-upgrade$(NC) - Применение миграций"
	@echo "  $(YELLOW)migrate-downgrade$(NC) - Откат миграций"
	@echo "  $(YELLOW)setup-db$(NC)       - Настройка базы данных"
	@echo "  $(YELLOW)delete-user$(NC)    - Удаление пользователя"
	@echo "  $(YELLOW)format$(NC)         - Форматирование кода"
	@echo "  $(YELLOW)lint$(NC)           - Проверка кода"
	@echo "  $(YELLOW)check$(NC)          - Полная проверка проекта"

# Установка зависимостей
install:
	@echo "$(GREEN)Установка зависимостей...$(NC)"
	$(PIP) install -r requirements.txt

# Установка зависимостей для разработки
install-dev:
	@echo "$(GREEN)Установка зависимостей для разработки...$(NC)"
	$(PIP) install -r requirements.txt
	$(PIP) install black flake8 mypy pytest pytest-cov

# Запуск приложения в production режиме
run:
	@echo "$(GREEN)Запуск приложения в production режиме...$(NC)"
	$(UVICORN) $(APP_MODULE) --host $(HOST) --port $(PORT) --workers $(WORKERS)

# Запуск приложения в development режиме
run-dev:
	@echo "$(GREEN)Запуск приложения в development режиме...$(NC)"
	$(UVICORN) $(APP_MODULE) --reload --host $(HOST) --port $(PORT)

# Запуск всех тестов
test:
	@echo "$(GREEN)Запуск всех тестов...$(NC)"
	$(PYTHON_VENV) -m pytest tests/ -v --disable-warnings

# Запуск unit тестов
test-unit:
	@echo "$(GREEN)Запуск unit тестов...$(NC)"
	$(PYTHON_VENV) -m pytest tests/unit/ -v --disable-warnings

# Запуск integration тестов
test-integration:
	@echo "$(GREEN)Запуск integration тестов...$(NC)"
	$(PYTHON_VENV) -m pytest tests/integration/ -v --disable-warnings

# Запуск end-to-end тестов
test-e2e:
	@echo "$(GREEN)Запуск end-to-end тестов...$(NC)"
	$(PYTHON_VENV) -m pytest tests/e2e/ -v --disable-warnings

# Запуск тестов с покрытием
test-coverage:
	@echo "$(GREEN)Запуск тестов с покрытием...$(NC)"
	$(PYTHON_VENV) -m pytest tests/ --cov=app --cov-report=html --cov-report=term --disable-warnings

# Очистка кэша и временных файлов
clean:
	@echo "$(GREEN)Очистка кэша и временных файлов...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage

# Создание новой миграции
migrate:
	@echo "$(GREEN)Создание новой миграции...$(NC)"
	@read -p "Введите сообщение для миграции: " message; \
	$(ALEMBIC) revision --autogenerate -m "$$message"

# Применение миграций
migrate-upgrade:
	@echo "$(GREEN)Применение миграций...$(NC)"
	$(ALEMBIC) upgrade head

# Откат миграций
migrate-downgrade:
	@echo "$(GREEN)Откат миграций...$(NC)"
	$(ALEMBIC) downgrade -1

# Настройка базы данных
setup-db:
	@echo "$(GREEN)Настройка базы данных...$(NC)"
	PYTHONPATH=. $(PYTHON_VENV) scripts/setup_db.py

# Удаление пользователя
delete-user:
	@echo "$(GREEN)Удаление пользователя...$(NC)"
	@read -p "Введите email пользователя для удаления: " email; \
	PYTHONPATH=. $(PYTHON_VENV) scripts/delete_user.py "$$email"

# Форматирование кода
format:
	@echo "$(GREEN)Форматирование кода...$(NC)"
	$(PYTHON_VENV) -m black app/ tests/ scripts/

# Проверка кода
lint:
	@echo "$(GREEN)Проверка кода...$(NC)"
	$(PYTHON_VENV) -m flake8 app/ tests/ scripts/
	$(PYTHON_VENV) -m black --check app/ tests/ scripts/

# Полная проверка проекта
check: lint test
	@echo "$(GREEN)Полная проверка проекта завершена!$(NC)"

# Создание виртуального окружения
venv:
	@echo "$(GREEN)Создание виртуального окружения...$(NC)"
	$(PYTHON) -m venv $(VENV)
	@echo "$(GREEN)Виртуальное окружение создано. Активируйте его:$(NC)"
	@echo "$(YELLOW)source $(VENV)/bin/activate$(NC)"

# Активация виртуального окружения (только для Unix/Linux/macOS)
activate:
	@echo "$(GREEN)Активация виртуального окружения...$(NC)"
	@echo "$(YELLOW)Выполните: source $(VENV)/bin/activate$(NC)"

# Проверка здоровья приложения
health:
	@echo "$(GREEN)Проверка здоровья приложения...$(NC)"
	curl -f http://localhost:$(PORT)/health || echo "$(RED)Приложение не отвечает$(NC)"

# Запуск тестового email сервиса
test-email:
	@echo "$(GREEN)Тестирование email сервиса...$(NC)"
	PYTHONPATH=. $(PYTHON_VENV) scripts/test_real_email.py

# Запуск ручного тестирования API
test-api-manual:
	@echo "$(GREEN)Ручное тестирование API...$(NC)"
	PYTHONPATH=. $(PYTHON_VENV) scripts/test_api_manual.py

# Тестирование импортов
test-imports:
	@echo "$(GREEN)Тестирование импортов...$(NC)"
	PYTHONPATH=. $(PYTHON_VENV) scripts/test_imports.py

# Создание резервной копии базы данных
backup-db:
	@echo "$(GREEN)Создание резервной копии базы данных...$(NC)"
	@read -p "Введите имя файла для резервной копии: " filename; \
	pg_dump -h localhost -U postgres -d fastapi_db > "$$filename"

# Восстановление базы данных из резервной копии
restore-db:
	@echo "$(GREEN)Восстановление базы данных...$(NC)"
	@read -p "Введите имя файла резервной копии: " filename; \
	psql -h localhost -U postgres -d fastapi_db < "$$filename"

# Показать логи приложения
logs:
	@echo "$(GREEN)Логи приложения (если запущено через systemd)...$(NC)"
	journalctl -u fastapi-app -f

# Остановка приложения
stop:
	@echo "$(GREEN)Остановка приложения...$(NC)"
	pkill -f uvicorn || echo "$(YELLOW)Приложение не запущено$(NC)"

# Перезапуск приложения
restart: stop
	@echo "$(GREEN)Перезапуск приложения...$(NC)"
	$(MAKE) run-dev

# Информация о проекте
info:
	@echo "$(GREEN)Информация о проекте:$(NC)"
	@echo "  Python: $(shell $(PYTHON_VENV) --version)"
	@echo "  FastAPI: $(shell $(PYTHON_VENV) -c 'import fastapi; print(fastapi.__version__)')"
	@echo "  Uvicorn: $(shell $(PYTHON_VENV) -c 'import uvicorn; print(uvicorn.__version__)')"
	@echo "  SQLAlchemy: $(shell $(PYTHON_VENV) -c 'import sqlalchemy; print(sqlalchemy.__version__)')"
	@echo "  Alembic: $(shell $(PYTHON_VENV) -c 'import alembic; print(alembic.__version__)')" 
