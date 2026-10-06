# 🔧 TROUBLESHOOTING GUIDE

## ❌ Error: "This site can't be reached - ERR_CONNECTION_REFUSED"

This means the server isn't running yet. Follow these steps:

---

### ✅ SOLUTION - Start Services Manually

**Open Command Prompt #1** (Backend):

```cmd
cd C:\Users\SOHAM\Desktop\SIH_2026\backend

REM Activate virtual environment
venv\Scripts\activate.bat

REM If venv doesn't exist, create it first:
REM python -m venv venv
REM venv\Scripts\activate.bat
REM pip install -r requirements.txt

REM Start the API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**WAIT** until you see:
```
INFO:     Application startup complete.
```

**Open Command Prompt #2** (Frontend):

```cmd
cd C:\Users\SOHAM\Desktop\SIH_2026\frontend

python serve.py
```

**NOW** open browser: http://localhost:3000

---

## 🐍 Error: "python: command not found"

### Solution:
1. Install Python from https://www.python.org/downloads/
2. **IMPORTANT:** Check "Add Python to PATH" during installation
3. Restart Command Prompt
4. Try again

---

## 📦 Error: "pip: command not found"

### Solution:
```cmd
python -m ensurepip --upgrade
python -m pip install --upgrade pip
```

---

## 🔒 Error: "Permission denied" or "Access denied"

### Solution:
1. Run Command Prompt as Administrator
   - Right-click Command Prompt
   - Select "Run as administrator"
2. Try the commands again

---

## 🐳 Error: Docker not running

### Solution:
1. Open Docker Desktop
2. Wait for it to show "Docker Desktop is running"
3. Check with: `docker ps`
4. Then run: `docker-compose up -d postgres redis minio`

---

## 🔌 Error: "Port 8000 is already in use"

### Solution 1: Kill the process
```cmd
netstat -ano | findstr :8000
REM Note the PID (last number)
taskkill /PID <number> /F
```

### Solution 2: Use different port
```cmd
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

Then update `frontend/index.html`:
```javascript
const API_BASE = 'http://localhost:8001';  // Change from 8000 to 8001
```

---

## 💾 Error: Database connection failed

### Solution:
```cmd
REM Check if PostgreSQL is running
docker ps | findstr postgres

REM If not running, start it
docker-compose up -d postgres

REM Wait 10 seconds
timeout /t 10

REM Try initializing again
cd backend
alembic upgrade head
python scripts\init_database.py
```

---

## 📚 Error: "No module named 'X'"

### Solution:
```cmd
cd C:\Users\SOHAM\Desktop\SIH_2026\backend
venv\Scripts\activate.bat
pip install -r requirements.txt
```

For specific modules:
```cmd
pip install groq
pip install fastapi
pip install uvicorn
pip install sqlalchemy
pip install alembic
```

---

## 🌐 Error: Frontend won't start

### Solution:
```cmd
cd C:\Users\SOHAM\Desktop\SIH_2026\frontend

REM Try on different port
python -m http.server 3001

REM Then open: http://localhost:3001/index.html
```

---

## 🔄 Error: "alembic: command not found"

### Solution:
```cmd
venv\Scripts\activate.bat
pip install alembic
alembic upgrade head
```

---

## 📝 Error: "Cannot find file 'app.main'"

### Solution:
Make sure you're in the correct directory:
```cmd
cd C:\Users\SOHAM\Desktop\SIH_2026\backend
dir
REM You should see: app, scripts, requirements.txt

python -c "import app.main"
REM If this works, uvicorn will work

uvicorn app.main:app --reload
```

---

## 🔑 Error: Groq API authentication failed

### Solution:
Check `.env` file:
```cmd
cd C:\Users\SOHAM\Desktop\SIH_2026
notepad .env
```

Make sure it has:
```
GROQ_API_KEY=<YOUR_GROQ_API_KEY>
LLM_PROVIDER=groq
```

---

## 🗄️ Error: Database migration failed

### Solution:
```cmd
cd backend

REM Reset database
docker-compose down -v
docker-compose up -d postgres
timeout /t 10

REM Reinitialize
alembic upgrade head
python scripts\init_database.py
```

---

## 🚫 Error: CORS policy blocking

### Solution:
Already configured in the code, but if needed:

Edit `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 💻 Error: Virtual environment activation failed

### Solution:

**PowerShell:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\Activate.ps1
```

**CMD:**
```cmd
venv\Scripts\activate.bat
```

**If still fails, don't use venv:**
```cmd
pip install -r backend\requirements.txt
cd backend
uvicorn app.main:app --reload
```

---

## 🔍 Quick Diagnostics

### Run Setup Test:
```cmd
cd C:\Users\SOHAM\Desktop\SIH_2026
python test_setup.py
```

### Check Docker:
```cmd
docker ps
REM Should show: orca-postgres, orca-redis, orca-minio
```

### Check Python:
```cmd
python --version
REM Should show: Python 3.8 or higher
```

### Check Ports:
```cmd
netstat -ano | findstr "8000 3000 5432 6379"
REM 5432 and 6379 should show (Docker)
REM 8000 and 3000 should show when services running
```

### Test API Manually:
```cmd
curl http://localhost:8000/health
REM Should return JSON with status
```

---

## 🆘 Nuclear Option (Fresh Start)

If nothing works, start completely fresh:

```cmd
REM 1. Stop everything
docker-compose down -v
taskkill /F /IM python.exe
taskkill /F /IM uvicorn.exe

REM 2. Clean up
cd C:\Users\SOHAM\Desktop\SIH_2026
rmdir /s /q backend\venv
rmdir /s /q backend\__pycache__
rmdir /s /q backend\app\__pycache__

REM 3. Restart Docker Desktop

REM 4. Start fresh
docker-compose up -d postgres redis minio
timeout /t 30

REM 5. Setup Python
cd backend
python -m venv venv
venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt

REM 6. Initialize database
alembic upgrade head
python scripts\init_database.py

REM 7. Start services
uvicorn app.main:app --reload

REM 8. In NEW window - frontend
cd ..\frontend
python serve.py
```

---

## ✅ Verification Checklist

Before starting ORCA, verify:

- [ ] Docker Desktop is running
- [ ] `docker ps` shows 3 containers
- [ ] Python 3.8+ installed
- [ ] `.env` file exists with credentials
- [ ] `backend/app` directory exists
- [ ] `frontend/index.html` exists
- [ ] Ports 8000, 3000 are free
- [ ] No antivirus blocking connections

---

## 📞 Still Stuck?

1. **Run diagnostics:**
   ```cmd
   python test_setup.py
   ```

2. **Check logs:**
   - Backend: Look at terminal running uvicorn
   - Docker: `docker-compose logs`
   - Frontend: Look at terminal running serve.py

3. **Common issues:**
   - Docker not running → Start Docker Desktop
   - Python not found → Install Python
   - Port in use → Use different port
   - Module not found → Install dependencies

---

## 🎯 Working Configuration

If everything is correct, you should see:

**Terminal 1 (Backend):**
```
INFO: Uvicorn running on http://0.0.0.0:8000
INFO: Application startup complete.
```

**Terminal 2 (Frontend):**
```
Server running at: http://localhost:3000
```

**Browser (http://localhost:3000):**
- ORCA dashboard loads
- Green status badge
- Chat interface works

---

**If you follow this guide step by step, ORCA WILL work!** 🚀
