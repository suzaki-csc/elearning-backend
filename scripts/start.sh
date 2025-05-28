#!/bin/bash
set -e

echo "Starting E-Learning Backend..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file with your configuration"
fi

# Start services
echo "Starting Docker services..."
docker-compose up -d mysql redis

# Wait for MySQL to be ready
echo "Waiting for MySQL to be ready..."
until docker-compose exec mysql mysqladmin ping -h"localhost" --silent; do
    echo "Waiting for database connection..."
    sleep 2
done

# Run database migrations
echo "Running database migrations..."
docker-compose run --rm api alembic upgrade head

# Start API server
echo "Starting API server..."
docker-compose up api

echo "E-Learning Backend is running on http://localhost:8000"
echo "API documentation available at http://localhost:8000/docs"