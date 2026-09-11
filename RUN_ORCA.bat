@echo off
echo ========================================
echo    ORCA MARINE INTELLIGENCE PLATFORM
echo ========================================
echo.

REM Check if Docker is running
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo [1/6] Starting Docker services...
echo.
docker-compose up -d postgres redis minio
if %errorlevel% neq 0 (
    echo ERROR: Failed to start Docker services
    pause
    exit /b 1
)

echo.
echo [2/6] Waiting for services to be ready (30 seconds)...
timeout /t 30 /nobreak >nul

echo.
echo [3/6] Checking Python environment...
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo.
echo [4/6] Installing/Updating dependencies...
call venv\Scripts\activate.bat
cd backend
pip install --quiet groq
pip install --quiet -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [5/6] Initializing database...
alembic upgrade head 2>nul
python scripts\init_database.py

echo.
echo [6/6] Starting ORCA services...
echo.

REM Start API server in new window
start "ORCA API Server" cmd /k "cd /d %CD% && venv\Scripts\activate.bat && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a bit for API to start
timeout /t 5 /nobreak >nul

REM Start frontend in new window
cd ..
start "ORCA Frontend Dashboard" cmd /k "cd /d %CD%\frontend && python serve.py"

echo.
echo ========================================
echo     ORCA IS NOW RUNNING!
echo ========================================
echo.
echo API Server:     http://localhost:8000
echo API Docs:       http://localhost:8000/docs
echo Frontend:       http://localhost:3000
echo.
echo The dashboard will open automatically in your browser.
echo.
echo To stop ORCA:
echo   1. Close the API and Frontend windows
echo   2. Run: docker-compose down
echo.
echo ========================================
pause
