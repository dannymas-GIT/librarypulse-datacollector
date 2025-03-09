#!/bin/bash

set -e

# Check if the virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup..."
    ./setup.sh
fi

# Activate the virtual environment
source venv/bin/activate

# Check if the database needs to be initialized
if [ ! -f "backend/.env" ]; then
    echo "Environment file not found. Creating from example..."
    cp backend/.env.example backend/.env
    
    # Generate a random secret key
    secret_key=$(openssl rand -base64 32)
    sed -i "s/SECRET_KEY=changeme_use_openssl_rand_base64_32/SECRET_KEY=$secret_key/" backend/.env
fi

# Create logs directory if it doesn't exist
mkdir -p backend/logs

# Initialize the database
echo "Initializing the database..."
cd backend
python init_db.py

# Start the API server
echo "Starting the API server..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 