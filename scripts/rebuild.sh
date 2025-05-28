#!/bin/bash
set -e

echo "Rebuilding E-Learning Backend from scratch..."

# Run clean script
./scripts/clean.sh

# Wait a moment for cleanup to complete
sleep 2

# Run build with clean flag
./scripts/build.sh --clean

echo "Rebuild completed successfully!"