.PHONY: setup setup-dev docker-build docker-start docker-stop docker-logs test lint clean

# Application settings
APP_NAME = librarypulse
PYTHON = python
PIP = pip
PYTEST = pytest
ALEMBIC = alembic

setup:
	@echo "Setting up the IMLS Library Pulse project..."
	@chmod +x setup.sh
	@./setup.sh

setup-dev: setup
	@echo "Installing development dependencies..."
	@cd backend && $(PIP) install -r requirements.txt
	@$(PIP) install black isort flake8 mypy pytest pytest-cov
	@echo "Setup complete!"

start-api:
	@echo "Starting the API server..."
	@cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

docker-build:
	@echo "Building Docker containers..."
	@docker-compose build

docker-start:
	@echo "Starting Docker containers..."
	@docker-compose up -d

docker-stop:
	@echo "Stopping Docker containers..."
	@docker-compose down

docker-logs:
	@echo "Showing Docker logs..."
	@docker-compose logs -f

alembic-init:
	@echo "Initializing Alembic migrations..."
	@cd backend && $(ALEMBIC) init alembic

alembic-migrate:
	@echo "Creating a new migration..."
	@cd backend && $(ALEMBIC) revision --autogenerate -m "$(message)"

alembic-upgrade:
	@echo "Applying migrations..."
	@cd backend && $(ALEMBIC) upgrade head

alembic-downgrade:
	@echo "Rolling back the last migration..."
	@cd backend && $(ALEMBIC) downgrade -1

collect-data:
	@echo "Collecting data from IMLS..."
	@cd backend && $(PYTHON) -m app.collector --$(action)

test:
	@echo "Running tests..."
	@cd backend && $(PYTEST) -v

test-cov:
	@echo "Running tests with coverage..."
	@cd backend && $(PYTEST) --cov=app --cov-report=html

lint:
	@echo "Running linters..."
	@cd backend && black . && isort . && flake8 .

clean:
	@echo "Cleaning up..."
	@find . -type d -name __pycache__ -exec rm -rf {} +
	@find . -type d -name *.egg-info -exec rm -rf {} +
	@find . -type d -name *.eggs -exec rm -rf {} +
	@find . -type f -name *.pyc -delete
	@find . -type f -name *.pyo -delete
	@find . -type f -name *.pyd -delete
	@rm -rf .pytest_cache
	@rm -rf .coverage
	@rm -rf htmlcov
	@rm -rf backend/build
	@rm -rf backend/dist
	@rm -rf backend/.pytest_cache
	@rm -rf backend/htmlcov
	@echo "Cleanup complete!"

help:
	@echo "Available commands:"
	@echo "  make setup              - Set up the project"
	@echo "  make setup-dev          - Set up the project for development"
	@echo "  make start-api          - Start the API server"
	@echo "  make docker-build       - Build Docker containers"
	@echo "  make docker-start       - Start Docker containers"
	@echo "  make docker-stop        - Stop Docker containers"
	@echo "  make docker-logs        - Show Docker logs"
	@echo "  make alembic-init       - Initialize Alembic migrations"
	@echo "  make alembic-migrate    - Create a new migration (usage: make alembic-migrate message='description')"
	@echo "  make alembic-upgrade    - Apply migrations"
	@echo "  make alembic-downgrade  - Roll back the last migration"
	@echo "  make collect-data       - Collect data from IMLS (usage: make collect-data action=year=2022)"
	@echo "                                              or: make collect-data action=all-years"
	@echo "                                              or: make collect-data action=update"
	@echo "  make test               - Run tests"
	@echo "  make test-cov           - Run tests with coverage"
	@echo "  make lint               - Run linters"
	@echo "  make clean              - Clean up temporary files" 