.PHONY: help install test lint format run clean docker-build docker-run init-data examples

help:
	@echo "Available commands:"
	@echo "  install      - Install dependencies"
	@echo "  test         - Run tests"
	@echo "  test-unit    - Run unit tests only"
	@echo "  test-int     - Run integration tests only"
	@echo "  test-e2e     - Run end-to-end tests only"
	@echo "  lint         - Run linters"
	@echo "  format       - Format code"
	@echo "  run          - Run application"
	@echo "  init-data    - Initialize sample data"
	@echo "  examples     - Run usage examples"
	@echo "  clean        - Clean generated files"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run with Docker Compose"

install:
	pip install -r requirements.txt

test:
	pytest -v --cov=src --cov-report=html

test-unit:
	pytest tests/unit -v

test-int:
	pytest tests/integration -v

test-e2e:
	pytest tests/e2e -v

lint:
	ruff check src tests
	mypy src

format:
	black src tests
	ruff check --fix src tests

run:
	python main.py

init-data:
	python scripts/init_sample_data.py

examples:
	python examples/basic_usage.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov
	rm -rf data/

docker-build:
	docker-compose build

docker-run:
	docker-compose up -d
