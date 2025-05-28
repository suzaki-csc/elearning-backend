#!/bin/bash
set -e

echo "Fixing database tables..."

# Stop API server to avoid conflicts
echo "Stopping API server..."
docker-compose stop api

# Start database services
echo "Starting database services..."
docker-compose up -d mysql redis

# Wait for MySQL to be ready
echo "Waiting for MySQL to be ready..."
until docker-compose exec mysql mysqladmin ping -h"localhost" --silent; do
    echo "Waiting for database connection..."
    sleep 2
done

# Check current database state
echo "Checking database tables..."
docker-compose exec mysql mysql -u elearning -ppassword elearning_db -e "SHOW TABLES;"

# Remove existing alembic versions if any
echo "Cleaning up Alembic state..."
rm -rf alembic/versions/*

# Create new initial migration
echo "Creating initial migration..."
docker-compose run --rm api alembic revision --autogenerate -m "Initial migration with all tables"

# Apply migration
echo "Applying migration..."
docker-compose run --rm api alembic upgrade head

# Verify tables were created
echo "Verifying tables..."
docker-compose exec mysql mysql -u elearning -ppassword elearning_db -e "SHOW TABLES;"
docker-compose exec mysql mysql -u elearning -ppassword elearning_db -e "DESCRIBE users;"

echo "Database fix completed!"
echo "You can now restart the API server with: docker-compose up api"