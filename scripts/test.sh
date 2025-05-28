#!/bin/bash
set -e

echo "🧪 Running E-Learning Backend tests..."

# Function to cleanup on exit
cleanup() {
    echo "🧹 Cleaning up..."
    docker-compose down --volumes --remove-orphans
}
trap cleanup EXIT

# Start test dependencies
echo "🚀 Starting test dependencies..."
docker-compose up -d mysql redis

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
echo "Waiting for MySQL..."
until docker-compose exec mysql mysqladmin ping -h"localhost" --silent; do
    echo "MySQL is unavailable - sleeping"
    sleep 2
done
echo "✅ MySQL is ready!"

echo "Waiting for Redis..."
until docker-compose exec redis redis-cli ping; do
    echo "Redis is unavailable - sleeping"
    sleep 2
done
echo "✅ Redis is ready!"

# Build test image
echo "🔨 Building test image..."
docker-compose build test

# Run tests
echo "🧪 Running pytest..."
if docker-compose run --rm test; then
    echo "✅ Tests passed!"
else
    echo "❌ Tests failed!"
    exit 1
fi

# Run code quality checks
echo "🔍 Running code quality checks..."

# Black formatting check
echo "📝 Checking code formatting with Black..."
if docker-compose run --rm test black --check src tests; then
    echo "✅ Code formatting is correct!"
else
    echo "❌ Code formatting issues found!"
    echo "💡 Run 'poetry run black src tests' to fix formatting"
    exit 1
fi

# Flake8 linting
echo "🔍 Running flake8 linting..."
if docker-compose run --rm test flake8 src tests; then
    echo "✅ No linting issues found!"
else
    echo "❌ Linting issues found!"
    exit 1
fi

# MyPy type checking
echo "🔍 Running MyPy type checking..."
if docker-compose run --rm test mypy src; then
    echo "✅ Type checking passed!"
else
    echo "❌ Type checking issues found!"
    exit 1
fi

# Bandit security check
echo "🔒 Running Bandit security check..."
if docker-compose run --rm test bandit -r src; then
    echo "✅ No security issues found!"
else
    echo "❌ Security issues found!"
    exit 1
fi

echo "🎉 All tests and checks completed successfully!"