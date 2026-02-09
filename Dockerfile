# ==============================================================================
# Anupam Dutta Portfolio - Production Dockerfile
# Multi-stage build for minimal production image
# ==============================================================================

# ---- Stage 1: Build ----
FROM python:3.12-slim as builder

WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements/production.txt /app/requirements.txt
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Stage 2: Production ----
FROM python:3.12-slim

# Security: run as non-root user
RUN groupadd -r portfolio && useradd -r -g portfolio -d /app -s /sbin/nologin portfolio

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . /app/

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media /app/logs \
    && chown -R portfolio:portfolio /app

# Collect static files
RUN DJANGO_SETTINGS_MODULE=config.settings.production \
    SECRET_KEY=build-secret-not-used \
    DATABASE_URL=sqlite:///tmp/build.db \
    python manage.py collectstatic --noinput 2>/dev/null || true

# Switch to non-root user
USER portfolio

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Start gunicorn
CMD ["gunicorn", \
     "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--worker-class", "gthread", \
     "--threads", "2", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info"]
