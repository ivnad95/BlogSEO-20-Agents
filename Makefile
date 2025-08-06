# Makefile for BlogSEO v3
# Development automation and task management

.PHONY: help install run lint format test clean setup-pre-commit

# Default target - show help
help:
	@echo "BlogSEO v3 Development Makefile"
	@echo "================================"
	@echo ""
	@echo "Available commands:"
	@echo "  make install        - Install dependencies and set up development environment"
	@echo "  make run           - Run the Streamlit application"
	@echo "  make lint          - Run linting checks (flake8)"
	@echo "  make format        - Auto-format code (black, isort)"
	@echo "  make test          - Run test suite"
	@echo "  make clean         - Clean cache and temporary files"
	@echo "  make setup-pre-commit - Install and configure pre-commit hooks"
	@echo ""

# Install dependencies and set up development environment
install:
	@echo "Installing dependencies..."
	pip install --upgrade pip
	pip install -r requirements.txt
	@echo ""
	@echo "Installing development tools..."
	@if [ -f requirements-dev.txt ]; then \
		echo "Installing from requirements-dev.txt..."; \
		pip install -r requirements-dev.txt; \
	else \
		echo "Installing essential dev tools..."; \
		pip install black isort flake8 pre-commit pytest; \
	fi
	@echo ""
	@echo "Setting up pre-commit hooks..."
	pre-commit install
	@echo ""
	@echo "Creating .env file from template..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Created .env file. Please update it with your API keys."; \
	else \
		echo "⚠️  .env file already exists. Skipping..."; \
	fi
	@echo ""
	@echo "✅ Installation complete!"

# Run the Streamlit application
run:
	@echo "Starting BlogSEO v3 application..."
	streamlit run app.py

# Run linting checks
lint:
	@echo "Running flake8 linting checks..."
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics \
		--exclude=venv,__pycache__,.git,cache,output

# Auto-format code
format:
	@echo "Formatting code with black..."
	black . --line-length=100 --exclude="venv|__pycache__|.git|cache|output"
	@echo ""
	@echo "Sorting imports with isort..."
	isort . --profile black --line-length=100 --skip-glob="venv/*" --skip-glob="cache/*" --skip-glob="output/*"
	@echo ""
	@echo "✅ Code formatting complete!"

# Run test suite
test:
	@echo "Running test suite..."
	@if command -v pytest >/dev/null 2>&1; then \
		pytest tests/ -v --tb=short; \
	else \
		python -m pytest tests/ -v --tb=short; \
	fi

# Clean cache and temporary files
clean:
	@echo "Cleaning cache and temporary files..."
	@echo "Removing Python cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name "*.pyd" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo ""
	@echo "Cleaning application cache..."
	@if [ -d "cache" ]; then \
		rm -f cache/*.json 2>/dev/null || true; \
		rm -f cache/*.pkl 2>/dev/null || true; \
		rm -f cache/*.tmp 2>/dev/null || true; \
		echo "✅ Cache directory cleaned"; \
	fi
	@echo ""
	@echo "✅ Cleanup complete!"

# Setup pre-commit hooks only
setup-pre-commit:
	@echo "Installing pre-commit..."
	pip install pre-commit
	@echo "Setting up pre-commit hooks..."
	pre-commit install
	@echo "Running pre-commit on all files..."
	pre-commit run --all-files || true
	@echo "✅ Pre-commit setup complete!"
