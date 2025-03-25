#!/bin/bash
# Script to update the Library Lens application on Lightsail VPS

set -e  # Exit on error

echo "🚀 Updating Library Lens on VPS..."

# Save the current directory
CURRENT_DIR=$(pwd)

# Pull the latest changes
echo "📥 Pulling latest changes from git..."
git pull

# Rebuild the frontend
echo "🔨 Rebuilding frontend..."
cd frontend
npm ci
npm run build
cd "$CURRENT_DIR"

# Rebuild and restart containers
echo "🐳 Restarting Docker containers..."
docker-compose down
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."
curl -s http://localhost:8000/health || echo "❌ Backend health check failed"
curl -s -I http://localhost:3000 | grep -c "200" || echo "❌ Frontend check failed"

echo "✅ Update completed!" 