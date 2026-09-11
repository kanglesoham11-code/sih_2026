@echo off
echo ========================================
echo    ORCA - Marine Intelligence Platform
echo    Complete Startup Script
echo ========================================
echo.

:: Check if Docker is running
echo [1/6] Checking Docker...
docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)
echo Docker is running ✓
echo.

:: Start Docker services
echo [2/6] Starting Docker services (PostgreSQL, Redis, MinIO)...
docker-compose up -d
if errorlevel 1 (
    echo ERROR: Failed to start Docker services!
    pause
    exit /b 1
)
echo Docker services started ✓
echo.

:: Wait for services to be ready
echo [3/6] Waiting for services to initialize (10 seconds)...
timeout /t 10 /nobreak >nul
echo Services ready ✓
echo.

:: Install frontend dependencies if needed
if not exist "frontend\node_modules" (
    echo [4/6] Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
    echo Frontend dependencies installed ✓
    echo.
) else (
    echo [4/6] Frontend dependencies already installed ✓
    echo.
)

:: Start backend server
echo [5/6] Starting backend server...
start "ORCA Backend" cmd /k "cd backend && if exist venv\Scripts\activate.bat (venv\Scripts\activate.bat) && pip install -q -r requirements.txt && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak >nul
echo Backend server starting... ✓
echo.

:: Start frontend server
echo [6/6] Starting frontend server...
start "ORCA Frontend" cmd /k "cd frontend && npm run dev"
echo Frontend server starting... ✓
echo.

echo ========================================
echo    ORCA Started Successfully!
echo ========================================
echo.
echo Backend API:  http://localhost:8000
echo Frontend UI:  http://localhost:3000
echo.
echo Both servers are starting in separate windows.
echo Wait 30 seconds for full initialization.
echo.
echo Press Ctrl+C in each window to stop servers.
echo Close this window when done.
echo ========================================
pause
