#!/bin/bash

# OpenCosts Application Runner
# This script executes the backend to generate data and launches the frontend

set -e  # Exit on any error

echo "🚀 Starting OpenCosts Application..."

# Change to docker directory for compose operations
cd "$(dirname "$0")/../docker"

echo "📊 Step 1: Running data scraper to generate fresh data..."
# Run the scraper service to generate data
docker compose run --rm scraper

echo "✅ Data generation complete!"

echo "🔧 Step 2: Building and starting backend service..."
# Build and start backend service
docker compose up -d backend --build

echo "🎨 Step 3: Building and starting frontend service..."
# Build and start frontend service  
docker compose up -d frontend --build

echo "🌐 Application is now running!"
echo "   Backend API: http://localhost:8000"
echo "   Frontend UI: http://localhost:5173"
echo ""
echo "📋 To view logs:"
echo "   Backend logs:  docker compose logs backend -f"
echo "   Frontend logs: docker compose logs frontend -f"
echo ""
echo "🛑 To stop the application:"
echo "   docker compose down"
