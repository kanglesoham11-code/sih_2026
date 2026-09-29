#!/bin/bash
set -e

# Ensure logs directory exists for loguru file handlers
mkdir -p logs

export PYTHONPATH=/app

# Run migrations
echo "Running Alembic migrations..."
alembic upgrade head

# Start API
echo "Starting Uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
