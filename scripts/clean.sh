#!/bin/bash
set -e

echo "Cleaning up E-Learning Backend Docker resources..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running"
    exit 1
fi

# Stop all running containers
echo "Stopping all containers..."
docker-compose down --volumes --remove-orphans 2>/dev/null || true

# Remove project-specific images
echo "Removing project images..."
docker images | grep elearning | awk '{print $3}' | xargs -r docker rmi -f 2>/dev/null || true

# Remove unused images, containers, networks, and build cache
echo "Cleaning up unused Docker resources..."
docker system prune -af --volumes

# Remove MySQL and Redis data volumes
echo "Removing data volumes..."
docker volume rm elearning-backend_mysql_data 2>/dev/null || true
docker volume rm elearning-backend_redis_data 2>/dev/null || true

echo "Cleanup completed!"
echo ""
echo "To rebuild the project:"
echo "  ./scripts/build.sh"