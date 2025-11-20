# Multi-stage build for Watchtower Agent
FROM python:3.12-slim AS builder

WORKDIR /build

# Install dependencies in a virtual environment
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.12-slim

# Install systemd utilities for journalctl access
RUN apt-get update && \
    apt-get install -y --no-install-recommends systemd && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user (will need to be in systemd-journal group)
RUN groupadd -r watchtower && \
    useradd -r -g watchtower -G systemd-journal -s /sbin/nologin watchtower

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy agent script
COPY watchtower_agent.py .

# Change ownership
RUN chown -R watchtower:watchtower /app

# Switch to non-root user
USER watchtower

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Run the agent
CMD ["python", "watchtower_agent.py"]
