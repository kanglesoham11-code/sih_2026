@echo off
REM ORCA Development Startup Script (Windows)
REM Starts all services for local development

echo 🌊 Starting ORCA Development Environment...

REM Check if .env exists
if not exist .env (
    echo ⚠️  .env file not found!
    echo Copying .env.example to .env...
    copy .env.example .env
    echo ⚠️  Please edit .env with your credentials before continuing
    exit /b 1
)

REM Start infrastructure services
echo 📦 Starting infrastructure services (PostgreSQL, Redis, MinIO)...
docker-compose up -d postgres redis minio

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Check if virtual environment exists
if not exist venv (
    echo 📦 Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📦 Installing Python dependencies...
pip install -r backend\requirements.txt

REM Run database migrations
echo 🗄️  Running database migrations...
cd backend
alembic upgrade head

REM Initialize database with seed data
echo 🌱 Seeding database...
python scripts\init_database.py

REM Start services in new windows
echo 🚀 Starting services...

REM Start FastAPI backend
start "ORCA API" cmd /k "venv\Scripts\activate.bat && cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a moment
timeout /t 3 /nobreak >nul

REM Start Celery worker
start "ORCA Celery Worker" cmd /k "venv\Scripts\activate.bat && cd backend && celery -A app.workers.celery_app worker -l info"

REM Start Celery beat
start "ORCA Celery Beat" cmd /k "venv\Scripts\activate.bat && cd backend && celery -A app.workers.celery_app beat -l info"

cd ..

echo.
echo ✅ ORCA Development Environment Started!
echo.
echo 📍 Services:
echo   - API:      http://localhost:8000
echo   - Docs:     http://localhost:8000/docs
echo   - MinIO:    http://localhost:9001
echo   - Postgres: localhost:5432
echo   - Redis:    localhost:6379
echo.
echo 🛑 To stop all services:
echo   - Close all command windows
echo   - Run: docker-compose down
echo.

pause
