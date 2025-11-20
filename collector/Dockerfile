# Multi-stage build for Watchtower Collector
FROM python:3.12-slim AS builder

WORKDIR /build

# Install dependencies in a virtual environment
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.12-slim

# Create non-root user
RUN groupadd -r watchtower && \
    useradd -r -g watchtower -s /sbin/nologin watchtower && \
    mkdir -p /var/lib/watchtower && \
    chown -R watchtower:watchtower /var/lib/watchtower

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy application code
COPY main.py models.py database.py ./

# Change ownership
RUN chown -R watchtower:watchtower /app

# Switch to non-root user
USER watchtower

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://127.0.0.1:8000/healthz', timeout=3)"

# Expose port
EXPOSE 8000

# Run uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
