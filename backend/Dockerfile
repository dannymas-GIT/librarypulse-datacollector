FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Create final image
FROM python:3.11-slim

# Create non-root user for security
RUN useradd -m appuser

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/.local/bin:$PATH"

WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder stage and install
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/* \
    && rm -rf /wheels

# Create necessary directories
RUN mkdir -p /app/app/api && chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser app app/
COPY --chown=appuser:appuser alembic alembic/
COPY --chown=appuser:appuser alembic.ini .

# Create health check endpoint
RUN echo 'from fastapi import APIRouter\n\
router = APIRouter()\n\
\n\
@router.get("/health")\n\
async def health_check():\n\
    return {"status": "healthy"}\n\
' > /app/app/api/health.py

# Update main.py to include health check
RUN echo '\nfrom app.api import health\napp.include_router(health.router)\n' >> /app/app/main.py

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check configuration
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 