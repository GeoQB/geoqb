# Multi-stage build for production-ready GeoQB API

# Stage 1: Builder
FROM python:3.9-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt

# Stage 2: Runtime
FROM python:3.9-slim

# Create non-root user
RUN groupadd -r geoqb -g 1000 && \
    useradd -r -g geoqb -u 1000 -m -s /sbin/nologin geoqb

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy wheels and install
COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache /wheels/* && rm -rf /wheels

# Copy application code
COPY app/ /app/app/
# Note: For production builds with pyGeoQB, build from parent directory:
# docker build -f geoqb-api/Dockerfile -t geoqb-api .
# Then uncomment the line below:
# COPY pyGeoQB/ /app/pyGeoQB/

# Change ownership to non-root user
RUN chown -R geoqb:geoqb /app

# Switch to non-root user
USER geoqb

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
