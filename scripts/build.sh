
#!/bin/bash
set -e

echo "Building E-Learning Backend..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running"
    exit 1
fi

# Build Docker images
echo "Building Docker images..."
docker-compose build

# Install Python dependencies
echo "Installing Python dependencies..."
if command -v poetry &> /dev/null; then
    poetry install
else
    echo "Poetry not found. Please install Poetry first."
    exit 1
fi

echo "Build completed successfully!"