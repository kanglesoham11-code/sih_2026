# ORCA Backend Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for PostGIS and scientific libraries
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libgdal-dev \
    libproj-dev \
    libgeos-dev \
    libspatialindex-dev \
    libhdf5-dev \
    libnetcdf-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make start script executable
RUN chmod +x /app/render-start.sh

# Create non-root user
RUN useradd -m -u 1000 orca && chown -R orca:orca /app
USER orca

# Expose port (Render sets PORT env var)
EXPOSE 8000

# Default command (can be overridden)
CMD ["/app/render-start.sh"]
