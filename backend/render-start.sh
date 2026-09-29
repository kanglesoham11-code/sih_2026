#!/bin/bash
set -e

# Wait for DB if necessary (optional, but good practice)
# Run migrations
echo "Running Alembic migrations..."
alembic upgrade head

# Start API
echo "Starting Uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
