# Rehau Neasmart 2.0 Gateway - Makefile

.PHONY: help install dev test coverage lint format clean docker-build docker-run docker-stop

# Default target
help:
	@echo "Rehau Neasmart 2.0 Gateway - Available commands:"
	@echo ""
	@echo "  make install      Install production dependencies"
	@echo "  make dev          Install development dependencies"
	@echo "  make test         Run all tests"
	@echo "  make coverage     Run tests with coverage report"
	@echo "  make lint         Run code linting"
	@echo "  make format       Format code with black"
	@echo "  make clean        Clean temporary files"
	@echo ""
	@echo "Docker commands:"
	@echo "  make docker-build Build Docker image"
	@echo "  make docker-run   Run Docker container"
	@echo "  make docker-stop  Stop Docker container"
	@echo ""
	@echo "Development:"
	@echo "  make run          Run application in development mode"
	@echo "  make run-prod     Run with Gunicorn (production)"

# Installation targets
install:
	pip install -r requirements.txt

dev: install
	pip install pytest pytest-cov black flake8 mypy

# Testing targets
test:
	pytest tests/ -v --no-cov

coverage:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

test-unit:
	pytest tests/unit/ -v --no-cov

test-integration:
	pytest tests/integration/ -v --no-cov

# Code quality targets
lint:
	flake8 src/ tests/ --max-line-length=100 --exclude=venv,__pycache__
	mypy src/ --ignore-missing-imports

format:
	black src/ tests/ --line-length=100

check: lint test

# Cleaning targets
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .mypy_cache/

# Running targets
run:
	cd src && python main.py

run-prod:
	cd src && gunicorn --config gunicorn_config.py main:app

# Docker targets
docker-build:
	docker build -t rehau-neasmart-gateway:latest .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-shell:
	docker exec -it rehau-neasmart-gateway /bin/sh

# Database operations
db-backup:
	cp data/registers.db data/registers_backup_$(shell date +%Y%m%d_%H%M%S).db

db-reset:
	rm -f data/registers.db
	@echo "Database reset. Will be recreated on next startup."

# Configuration
config-validate:
	python -c "import json; json.load(open('data/config.json'))" && echo "Configuration is valid"

config-example:
	cp env.example .env
	@echo "Created .env from env.example. Please update with your values."

# Development helpers
shell:
	cd src && python -i -c "from main import *"

debug:
	NEASMART_LOG_LEVEL=DEBUG make run

# Release targets
version:
	@grep -E "version|Version" README.md src/main.py | head -5

# Quick start for new developers
quickstart: dev config-example
	@echo ""
	@echo "✅ Development environment ready!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Edit .env with your configuration"
	@echo "2. Run 'make test' to verify setup"
	@echo "3. Run 'make run' to start the application" 