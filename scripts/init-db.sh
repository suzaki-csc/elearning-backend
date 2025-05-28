#!/bin/bash
set -e

echo "Initializing database and Alembic..."

# Create alembic directory structure if it doesn't exist
if [ ! -d "alembic" ]; then
    echo "Creating Alembic directory structure..."
    mkdir -p alembic/versions
fi

# Start database services
echo "Starting database services..."
docker-compose up -d mysql redis

# Wait for MySQL to be ready
echo "Waiting for MySQL to be ready..."
until docker-compose exec mysql mysqladmin ping -h"localhost" --silent; do
    echo "Waiting for database connection..."
    sleep 2
done

# Create initial migration if versions directory is empty
if [ ! "$(ls -A alembic/versions 2>/dev/null)" ]; then
    echo "Creating initial migration..."
    docker-compose run --rm api alembic revision --autogenerate -m "Initial migration"
fi

# Apply migrations
echo "Applying database migrations..."
docker-compose run --rm api alembic upgrade head

echo "Database initialization completed!"