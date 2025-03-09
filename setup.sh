#!/bin/bash

set -e

echo "Setting up IMLS Library Pulse Data Collector..."

# Check if Python 3.11+ is installed
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11.0"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.11 or higher is required"
    echo "Current version: $python_version"
    exit 1
fi

# Create a virtual environment
echo "Creating a virtual environment..."
python3 -m venv venv

# Activate the virtual environment
echo "Activating the virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r backend/requirements.txt

# Create .env file if it doesn't exist
if [ ! -f backend/.env ]; then
    echo "Creating .env file..."
    cp backend/.env.example backend/.env
    
    # Generate a random secret key
    secret_key=$(openssl rand -base64 32)
    sed -i "s/SECRET_KEY=changeme_use_openssl_rand_base64_32/SECRET_KEY=$secret_key/" backend/.env
fi

# Create data directories
echo "Creating data directories..."
mkdir -p backend/data/raw backend/data/processed backend/logs

echo "Setup complete!"
echo ""
echo "To start the application:"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Start the API server:"
echo "   cd backend"
echo "   uvicorn app.main:app --reload"
echo ""
echo "   Or using Docker:"
echo "   docker-compose up -d"
echo ""
echo "3. Access the API documentation at:"
echo "   http://localhost:8000/docs"
echo ""
echo "4. To collect data, run:"
echo "   python -m app.collector --discover"
echo "   python -m app.collector --year 2022"
echo "   python -m app.collector --all-years"
echo "   python -m app.collector --update"
echo "" 