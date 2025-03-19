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

# Copy application code
COPY --chown=appuser:appuser . .

# Create a health check endpoint
RUN echo 'from fastapi import FastAPI, APIRouter\n\
router = APIRouter()\n\
@router.get("/health", tags=["health"])\n\
async def health_check():\n\
    return {"status": "healthy"}\n\
' > /app/app/api/health.py

# Make sure the health check endpoint is included in the API
RUN grep -q "from app.api import health" /app/app/api/__init__.py || \
    echo 'from app.api import health' >> /app/app/api/__init__.py && \
    grep -q "app.include_router(health.router)" /app/app/main.py || \
    sed -i '/app = FastAPI/a app.include_router(health.router)' /app/app/main.py

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 