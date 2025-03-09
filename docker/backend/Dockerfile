FROM python:3.11-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN addgroup --system app \
    && adduser --system --group app

# Copy requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend /app/

# Create data and logs directories and set permissions
RUN mkdir -p /app/data/raw /app/data/processed /app/logs \
    && chown -R app:app /app

# Switch to non-root user
USER app

# Create data directory
RUN mkdir -p /app/data

# Command to run when container starts
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 