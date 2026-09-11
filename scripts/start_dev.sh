#!/bin/bash
# ORCA Development Startup Script
# Starts all services for local development

set -e

echo "🌊 Starting ORCA Development Environment..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Copying .env.example to .env..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your credentials before continuing"
    exit 1
fi

# Start infrastructure services
echo "📦 Starting infrastructure services (PostgreSQL, Redis, MinIO)..."
docker-compose up -d postgres redis minio

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 5
until docker-compose exec -T postgres pg_isready -U orca; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 2
done
echo "✅ PostgreSQL is ready"

# Wait for Redis to be ready
echo "⏳ Waiting for Redis to be ready..."
until docker-compose exec -T redis redis-cli ping; do
    echo "Redis is unavailable - sleeping"
    sleep 2
done
echo "✅ Redis is ready"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r backend/requirements.txt

# Run database migrations
echo "🗄️  Running database migrations..."
cd backend
alembic upgrade head

# Initialize database with seed data
echo "🌱 Seeding database..."
python scripts/init_database.py

# Start backend API
echo "🚀 Starting FastAPI backend..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
API_PID=$!

# Start Celery worker
echo "⚙️  Starting Celery worker..."
celery -A app.workers.celery_app worker -l info &
WORKER_PID=$!

# Start Celery beat
echo "⏰ Starting Celery beat (scheduler)..."
celery -A app.workers.celery_app beat -l info &
BEAT_PID=$!

cd ..

echo ""
echo "✅ ORCA Development Environment Started!"
echo ""
echo "📍 Services:"
echo "  - API:      http://localhost:8000"
echo "  - Docs:     http://localhost:8000/docs"
echo "  - MinIO:    http://localhost:9001"
echo "  - Postgres: localhost:5432"
echo "  - Redis:    localhost:6379"
echo ""
echo "🛑 To stop all services:"
echo "  - Press Ctrl+C"
echo "  - Run: docker-compose down"
echo ""

# Wait for any process to exit
wait $API_PID $WORKER_PID $BEAT_PID
