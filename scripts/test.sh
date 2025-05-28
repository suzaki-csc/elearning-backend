#!/bin/bash
set -e

echo "Running E-Learning Backend tests..."

# Start test dependencies
echo "Starting test dependencies..."
docker-compose up -d mysql redis

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Run tests
echo "Running pytest..."
docker-compose run --rm test

# Run code quality checks
echo "Running code quality checks..."

# Black formatting check
echo "Checking code formatting with Black..."
docker-compose run --rm api black --check src tests

# Flake8 linting
echo "Running flake8 linting..."
docker-compose run --rm api flake8 src tests

# MyPy type checking
echo "Running MyPy type checking..."
docker-compose run --rm api mypy src

# Bandit security check
echo "Running Bandit security check..."
docker-compose run --rm api bandit -r src

echo "All tests and checks completed!"