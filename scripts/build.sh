#!/bin/bash
set -e

echo "Building E-Learning Backend..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running"
    exit 1
fi

# Parse command line arguments
CLEAN_BUILD=false
NO_CACHE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --clean)
            CLEAN_BUILD=true
            shift
            ;;
        --no-cache)
            NO_CACHE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --clean     Clean build (remove existing containers and images)"
            echo "  --no-cache  Build without using Docker cache"
            echo "  -h, --help  Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Clean build if requested
if [ "$CLEAN_BUILD" = true ]; then
    echo "Performing clean build..."
    
    # Stop and remove existing containers
    echo "Stopping existing containers..."
    docker-compose down --volumes --remove-orphans 2>/dev/null || true
    
    # Remove existing images
    echo "Removing existing images..."
    docker-compose down --rmi all --volumes --remove-orphans 2>/dev/null || true
    
    # Clean up unused Docker resources
    echo "Cleaning up Docker resources..."
    docker system prune -f
fi

# Build Docker images
BUILD_ARGS=""
if [ "$NO_CACHE" = true ] || [ "$CLEAN_BUILD" = true ]; then
    BUILD_ARGS="--no-cache --pull"
    echo "Building Docker images (no cache)..."
else
    echo "Building Docker images..."
fi

docker-compose build $BUILD_ARGS

# Install Python dependencies locally (if Poetry is available)
if command -v poetry &> /dev/null; then
    echo "Installing Python dependencies locally..."
    poetry install
else
    echo "Poetry not found. Skipping local dependency installation."
    echo "You can install Poetry from: https://python-poetry.org/docs/#installation"
fi

echo "Build completed successfully!"
echo ""
echo "Next steps:"
echo "  1. Copy .env.example to .env and configure your settings"
echo "  2. Run './scripts/start.sh' to start the application"
echo "  3. Run './scripts/test.sh' to run tests"
echo ""
echo "Build options:"
echo "  './scripts/build.sh --clean' for clean build"
echo "  './scripts/build.sh --no-cache' for build without cache"