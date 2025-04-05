#!/bin/bash
# Script to migrate development environment from "librarypulse" to "librarylens"
# This script should be run from /opt/projects/librarypulse/datacollector

set -e  # Exit on error

echo "🚀 Migrating development environment from librarypulse to librarylens..."

# Check if we're in the right directory
if [[ $(pwd) != "/opt/projects/librarypulse/datacollector" ]]; then
  echo "❌ Error: This script must be run from /opt/projects/librarypulse/datacollector"
  exit 1
fi

# Ensure services are running
echo "✅ Ensuring services are running..."
docker-compose up -d

# 1. Create a backup of the database
echo "📦 Creating database backup..."
docker-compose exec -T db pg_dump -U postgres librarypulse > librarypulse_backup.sql
echo "✅ Backup created as librarypulse_backup.sql"

# 2. Create a backup of docker-compose.yml
echo "📄 Creating backup of configuration files..."
cp docker-compose.yml docker-compose.yml.backup

# 3. Update docker-compose.yml with new database name
echo "🔄 Updating docker-compose.yml..."
sed -i 's/POSTGRES_DB=librarypulse/POSTGRES_DB=librarylens/g' docker-compose.yml
sed -i 's/DATABASE_URL=postgresql:\/\/postgres:postgres@db:5432\/librarypulse/DATABASE_URL=postgresql:\/\/postgres:postgres@db:5432\/librarylens/g' docker-compose.yml

# 4. Update any network or volume names if they exist
sed -i 's/librarypulse-network/librarylens-network/g' docker-compose.yml
sed -i 's/librarypulse-postgres-data/librarylens-postgres-data/g' docker-compose.yml

# 5. Stop services before recreating
echo "🛑 Stopping services..."
docker-compose down

# 6. Start services with new configuration
echo "🚀 Starting services with new configuration..."
docker-compose up -d

# 7. Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# 8. Create the new database and restore data
echo "🗄️ Creating new database and restoring data..."
docker-compose exec -T db psql -U postgres -c "CREATE DATABASE librarylens;"
cat librarypulse_backup.sql | docker-compose exec -T db psql -U postgres librarylens

# 9. Update backend environment variables if necessary
echo "🔄 Updating backend environment variables..."
if [ -f backend/.env ]; then
  sed -i 's/librarypulse/librarylens/g' backend/.env
fi

# 10. Restart services to apply all changes
echo "🔄 Restarting services..."
docker-compose restart

echo "✅ Migration completed successfully! Development environment now uses 'librarylens'"
echo ""
echo "Important next steps:"
echo "1. Update CI/CD pipelines to use 'librarylens' consistently"
echo "2. Verify all functionality in the development environment"
echo "3. Check for any hardcoded 'librarypulse' references in your code"

# List files that might need manual updating
echo ""
echo "Files that might contain 'librarypulse' references:"
grep -r "librarypulse" --include="*.py" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.yml" --include="*.env" . | grep -v "librarypulse_backup" || echo "No files found with librarypulse references." 