# STALWART Makefile
# Version: 1.0.0
# Date: 2026-02-16

.PHONY: help install dev-install test lint format clean docs run-dashboard run-api docker-build docker-run deploy data-prep

help:
	@echo "STALWART - Bridge Health Monitoring System"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  install          Install production dependencies"
	@echo "  dev-install      Install development dependencies"
	@echo "  test             Run tests"
	@echo "  lint             Run linters (flake8, mypy)"
	@echo "  format           Format code with black"
	@echo "  clean            Clean build artifacts"
	@echo "  docs             Build documentation"
	@echo "  run-dashboard    Run Streamlit dashboard"
	@echo "  run-api          Run FastAPI server"
	@echo "  docker-build     Build Docker image"
	@echo "  docker-run       Run Docker container"
	@echo "  deploy           Deploy to production"
	@echo "  data-prep        Prepare sample data"

install:
	pip install -r requirements.txt
	pip install -e .

dev-install:
	pip install -r requirements.txt
	pip install -e .[dev,ml,dashboard,field]

test:
	pytest tests/ -v --cov=src/stalwart --cov-report=term-missing

lint:
	flake8 src/ tests/
	mypy src/

format:
	black src/ tests/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf coverage.xml

docs:
	cd docs && make html
	@echo "Documentation built in docs/_build/html/"

run-dashboard:
	streamlit run src/stalwart/dashboard/app.py --server.port 8501

run-api:
	uvicorn src.stalwart.api.app:app --reload --host 0.0.0.0 --port 8000

docker-build:
	docker build -t stalwart:latest .

docker-run:
	docker run -p 8000:8000 -p 8501:8501 stalwart:latest

deploy:
	@echo "Deploying STALWART to production..."
	@echo "This script would deploy to your production environment"
	@echo "Options:"
	@echo "  make deploy TARGET=aws     # Deploy to AWS"
	@echo "  make deploy TARGET=gcp     # Deploy to Google Cloud"
	@echo "  make deploy TARGET=azure   # Deploy to Azure"

data-prep:
	python scripts/generate_sample_data.py --output data/samples/

.PHONY: version
version:
	@python -c "import stalwart; print(f'STALWART v{stalwart.__version__}')"

.PHONY: info
info:
	@echo "STALWART - Bridge Health Monitoring System"
	@echo "=========================================="
	@echo "Version: 1.0.0"
	@echo "Research Paper: Journal of Bridge Engineering (Feb 2026)"
	@echo "DOI: 10.5281/zenodo.18655299"
	@echo "Authors: Baladi, S., Johnson, R., Chen, M., Schmidt, K., Williams, S."
	@echo ""
	@echo "Bridges monitored: 47"
	@echo "Study duration: 36 months"
	@echo "Prediction accuracy: 94.7%"
	@echo "Early warning: 6-18 months"
	@echo ""
	@echo "For more information: https://stalwart-bridge.netlify.app"
