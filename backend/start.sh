#!/bin/bash

echo "Waiting for PostgreSQL..."
DB_HOST=$(echo $DATABASE_URL | sed -E "s/^postgresql:\/\/[^:]+:[^@]+@([^:]+):.*/\1/")
DB_PORT=$(echo $DATABASE_URL | sed -E "s/^postgresql:\/\/[^:]+:[^@]+@[^:]+:([0-9]+).*/\1/")

if [ -n "$DB_HOST" ] && [ -n "$DB_PORT" ]; then
    echo "Checking connection to PostgreSQL at $DB_HOST:$DB_PORT..."
    wait-for-it.sh -t 60 "$DB_HOST:$DB_PORT" -- echo "PostgreSQL is up!"
else
    echo "Could not parse DATABASE_URL: $DATABASE_URL"
fi

# Create necessary directories
mkdir -p /app/logs

# Set permissions
chown -R appuser:appuser /app/logs

# Run database migrations
echo "Running database migrations..."
cd /app && alembic upgrade head

# Create user tables if they don't exist
echo "Ensuring user tables are created..."
DB_NAME=$(echo $DATABASE_URL | sed -E "s/^postgresql:\/\/[^:]+:[^@]+@[^:]+:[0-9]+\/([^?]+).*/\1/")
DB_USER=$(echo $DATABASE_URL | sed -E "s/^postgresql:\/\/([^:]+):.*/\1/")
DB_PASSWORD=$(echo $DATABASE_URL | sed -E "s/^postgresql:\/\/[^:]+:([^@]+)@.*/\1/")
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f /app/create_user_tables.sql

# Start application
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 