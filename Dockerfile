# Youth Secure Check-in Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    gcc \
    libcups2-dev \
    wget \
    sqlite3 \
    libsqlcipher-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for database and uploads
RUN mkdir -p /app/data /app/uploads && \
    chmod 755 /app/data /app/uploads

# Expose port
EXPOSE 5000

# Environment variables (can be overridden)
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:5000/health || exit 1

# Run with gunicorn in production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "--timeout", "120", "wsgi:app"]
