# Stage 1: Builder
FROM python:3.12-slim AS builder

WORKDIR /app

# Install OS dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Run migrations and collect static
# RUN python manage.py makemigrations
# RUN python manage.py migrate
RUN python manage.py collectstatic --noinput

# Stage 2: Runtime
FROM python:3.12-slim

WORKDIR /app

# Create non-root user for security
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Copy installed dependencies from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code and collect static
COPY --from=builder /app /app

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DJANGO_SETTINGS_MODULE=subscription_apis.settings

# Expose port
EXPOSE 7000

# Run with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:7000", "subscription_apis.wsgi:application"]