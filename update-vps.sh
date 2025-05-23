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

# Update the docker-compose.yml file with the correct API URL
sed -i 's|VITE_API_URL=http://backend:8000/api/v1|VITE_API_URL=http://44.200.215.2:8000/api/v1|g' docker-compose.yml

# Rebuild and restart containers
echo "🐳 Restarting Docker containers..."
docker-compose down
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 15

# Ensure the admin user is created or updated
echo "👤 Ensuring admin user is set up correctly..."
# Copy the SQL script into the PostgreSQL container
docker cp backend/create_user_tables.sql datacollector_db_1:/tmp/create_user_tables.sql
# Run the script to create/update the users table
docker-compose exec -T db psql -U postgres -d librarypulse -f /tmp/create_user_tables.sql || echo "⚠️ Could not update user tables"
# Update the admin password directly as a fallback
docker-compose exec -T db psql -U postgres -d librarypulse -c "UPDATE users SET hashed_password = '\$2b\$12\$qFv2xVqe0jj5w9uSlyHmvOBB7FWpOPm/OGNrnM5VRSpHidZhmIdUS' WHERE username = 'admin';" || echo "⚠️ Could not update admin password"

# Restart the backend to ensure it picks up any database changes
echo "🔄 Restarting backend service..."
docker-compose restart backend
sleep 5

# Check if services are running
echo "🔍 Checking service status..."
curl -s http://localhost:8000/health || echo "❌ Backend health check failed"
curl -s -I http://localhost:3000 | grep -c "200" || echo "❌ Frontend check failed"

echo "✅ Update completed!" 