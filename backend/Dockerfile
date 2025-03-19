FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/data /app/extracted_data && \
    chown -R appuser:appuser /app

FROM python:3.11-slim

WORKDIR /app

# Copy from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl netcat-traditional postgresql-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

# Add wait-for-it script
RUN curl -s -o /usr/local/bin/wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh && \
    chmod +x /usr/local/bin/wait-for-it.sh

# Add startup script
RUN echo '#!/bin/bash\n\
echo "Waiting for PostgreSQL..."\n\
DB_HOST=$(echo $DATABASE_URL | sed -E "s/^postgresql:\\/\\/[^:]+:[^@]+@([^:]+):.*/\\1/")\n\
DB_PORT=$(echo $DATABASE_URL | sed -E "s/^postgresql:\\/\\/[^:]+:[^@]+@[^:]+:([0-9]+).*/\\1/")\n\
\n\
if [ -n "$DB_HOST" ] && [ -n "$DB_PORT" ]; then\n\
    echo "Checking connection to PostgreSQL at $DB_HOST:$DB_PORT..."\n\
    wait-for-it.sh -t 60 "$DB_HOST:$DB_PORT" -- echo "PostgreSQL is up!"\n\
else\n\
    echo "Could not parse DATABASE_URL: $DATABASE_URL"\n\
fi\n\
\n\
# Start application\n\
exec uvicorn app.main:app --host 0.0.0.0 --port 8000\n\
' > /app/start.sh && chmod +x /app/start.sh

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/data /app/extracted_data /app/logs && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Set health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["/app/start.sh"] 