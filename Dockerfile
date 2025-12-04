# ============
# Stage 1: Builder
# ============
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build-time dependencies if needed (currently not heavy)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# ============
# Stage 2: Runtime
# ============
FROM python:3.12-slim

# Set timezone to UTC
ENV TZ=UTC

WORKDIR /app

# Install system dependencies: cron + tzdata
RUN apt-get update && \
    apt-get install -y --no-install-recommends cron tzdata && \
    ln -snf /usr/share/zoneinfo/Etc/UTC /etc/localtime && \
    echo "Etc/UTC" > /etc/timezone && \
    rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local /usr/local

# Create volume mount points
RUN mkdir -p /data /cron && chmod 755 /data /cron

VOLUME ["/data", "/cron"]

# Copy application code (all .py and config files)
COPY . .

# Setup cron job
# - Copy cron file
# - Ensure LF line endings
# - Set proper permissions
# - Register with crontab
COPY cron/2fa-cron /etc/cron.d/totp-cron
RUN sed -i 's/\r$//' /etc/cron.d/totp-cron && \
    chmod 0644 /etc/cron.d/totp-cron && \
    crontab /etc/cron.d/totp-cron

# Expose API port
EXPOSE 8080

# Start cron service and API server
CMD ["sh", "-c", "cron && uvicorn api_service:app --host 0.0.0.0 --port 8080"]

