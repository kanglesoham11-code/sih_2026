# 🚀 MANUAL START GUIDE - STEP BY STEP

Follow these steps **EXACTLY** in order:

---

## ✅ Step 1: Docker Services (ALREADY DONE!)

Your Docker services are running:
- ✅ PostgreSQL (port 5432)
- ✅ Redis (port 6379)
- ✅ MinIO (port 9000, 9001)

**Skip to Step 2!**

---

## 🐍 Step 2: Setup Python Environment

**Open Command Prompt** and run these commands **ONE BY ONE**:

```cmd
cd C:\Users\SOHAM\Desktop\SIH_2026

python -m venv venv

venv\Scripts\activate.bat

cd backend

pip install groq

pip install -r requirements.txt
```

**Wait for installation to complete...**

---

## 🗄️ Step 3: Initialize Database

**Still in the same Command Prompt**, run:

```cmd
alembic upgrade head

python scripts\init_database.py
```

You should see:
```
✅ Database tables created
✅ Data sources seeded
✅ Marine boundaries seeded
```

---

## 🎯 Step 4: Start Backend API

**Keep the same Command Prompt open**, run:

```cmd
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**WAIT!** You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**✅ Keep this window open!**

---

## 🌐 Step 5: Start Frontend (NEW WINDOW)

**Open a NEW Command Prompt window**, run:

```cmd
cd C:\Users\SOHAM\Desktop\SIH_2026\frontend

python serve.py
```

You should see:
```
🌊 ORCA Frontend Dashboard
Server running at: http://localhost:3000
```

**✅ Keep this window open too!**

---

## 🧪 Step 6: Test!

**Open your browser and go to:**

http://localhost:3000

**You should see the ORCA dashboard!**

---

## 🔧 If Step 2 Fails (Python not found):

Check if Python is installed:
```cmd
python --version
```

If not installed:
1. Download from: https://www.python.org/downloads/
2. Install with "Add to PATH" checked
3. Try Step 2 again

---

## 🔧 If Step 4 Fails (Port 8000 in use):

Use a different port:
```cmd
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

Then update frontend to use port 8001:
- Edit `frontend/index.html`
- Change `API_BASE = 'http://localhost:8000'` to `API_BASE = 'http://localhost:8001'`

---

## ✅ Success Checklist:

- [ ] Docker containers running (check with `docker ps`)
- [ ] Virtual environment created and activated
- [ ] Dependencies installed
- [ ] Database initialized
- [ ] Backend running (port 8000)
- [ ] Frontend running (port 3000)
- [ ] Dashboard opens in browser

---

## 📸 What You Should See:

**In Backend Terminal:**
```
INFO:     Will watch for changes in these directories: ['C:\\Users\\SOHAM\\Desktop\\SIH_2026\\backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**In Frontend Terminal:**
```
🌊 ORCA Frontend Dashboard
==================================================
✅ Server running at: http://localhost:3000
✅ Dashboard: http://localhost:3000/index.html
==================================================
```

**In Browser:**
- Purple gradient header
- "ORCA Marine Intelligence Platform" title
- Green status badge
- Three info cards
- Chat interface

---

## 🆘 Still Having Issues?

**Check these:**

1. **Is Docker running?**
   ```cmd
   docker ps
   ```
   Should show 3 containers

2. **Is port 8000 free?**
   ```cmd
   netstat -ano | findstr :8000
   ```
   Should be empty

3. **Is Python working?**
   ```cmd
   python --version
   ```
   Should show Python 3.x

4. **Are you in the right directory?**
   ```cmd
   cd C:\Users\SOHAM\Desktop\SIH_2026\backend
   dir
   ```
   Should show `app`, `scripts`, `requirements.txt`

---

## 💡 Quick Troubleshooting:

### Error: "uvicorn: command not found"
**Fix:**
```cmd
venv\Scripts\activate.bat
pip install uvicorn
```

### Error: "alembic: command not found"
**Fix:**
```cmd
pip install alembic
```

### Error: "No module named 'app'"
**Fix:**
Make sure you're in the `backend` directory:
```cmd
cd C:\Users\SOHAM\Desktop\SIH_2026\backend
```

### Error: Database connection failed
**Fix:**
```cmd
docker-compose restart postgres
timeout /t 10
alembic upgrade head
```

---

## 🎯 After Everything Works:

### Test the API:
```cmd
curl http://localhost:8000/health
```

### Test the Dashboard:
Open: http://localhost:3000

### Test Chat:
Type in the chat box: "Hello!"

---

## 🌐 Get Live Link (After Everything Works):

1. **Download ngrok:** https://ngrok.com/download
2. **Extract** to Desktop
3. **Open new Command Prompt:**
   ```cmd
   cd C:\Users\SOHAM\Desktop\ngrok
   ngrok http 3000
   ```
4. **Copy the https:// link**
5. **Share it!**

---

**Follow these steps carefully and ORCA will run!** 🚀
