# 🚀 START ORCA - Complete Setup Guide

**Your credentials have been configured! Follow these steps to run and test ORCA.**

---

## ✅ Prerequisites Check

Make sure you have:
- [ ] Docker Desktop installed and running
- [ ] Python 3.12+ installed
- [ ] At least 8GB RAM available
- [ ] Ports free: 8000, 5432, 6379, 9000, 9001

---

## 📦 Step 1: Start Infrastructure (5 minutes)

Open Command Prompt or PowerShell in the project directory:

```cmd
cd C:\Users\SOHAM\Desktop\SIH_2026

# Start PostgreSQL, Redis, and MinIO
docker-compose up -d postgres redis minio

# Wait ~30 seconds for services to start
timeout /t 30 /nobreak

# Check if services are running
docker-compose ps
```

You should see 3 services running:
- ✅ orca-postgres (port 5432)
- ✅ orca-redis (port 6379)  
- ✅ orca-minio (ports 9000, 9001)

---

## 🐍 Step 2: Setup Python Environment (2 minutes)

```cmd
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate.bat

# Install dependencies
cd backend
pip install -r requirements.txt
```

---

## 🗄️ Step 3: Initialize Database (1 minute)

```cmd
# Still in backend directory

# Run migrations
alembic upgrade head

# Seed initial data (sources, boundaries)
python scripts\init_database.py
```

You should see:
```
✅ Database tables created
✅ Data sources seeded
✅ Marine boundaries seeded
```

---

## 🎯 Step 4: Start ORCA API (NOW!)

```cmd
# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Keep this terminal open!

---

## 🧪 Step 5: Test ORCA

### Test 1: Health Check

Open your browser or use curl:

**Browser:** http://localhost:8000/health

**Curl:**
```cmd
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "environment": "development",
  "version": "1.0.0"
}
```

### Test 2: API Documentation

**Open:** http://localhost:8000/docs

You should see the Swagger UI with all endpoints!

### Test 3: Test Agent Chat

```cmd
curl -X POST http://localhost:8000/api/v1/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"Hello! What can you help me with?\", \"mode\": \"standard\"}"
```

### Test 4: Check Data Sources

```cmd
curl http://localhost:8000/api/v1/sources
```

You should see registered sources including:
- ✅ incois_erddap
- ✅ imd_weather
- ✅ copernicus_marine (with YOUR credentials!)
- ✅ mosdac (with YOUR credentials!)

---

## 🌊 Your Live Credentials Are Configured!

The system is configured with:

- **Copernicus Marine:**
  - Username: `hershey`
  - Password: `Baviskar@2569`
  - Status: ✅ Ready to use

- **MOSDAC:**
  - Username: `godsplan`
  - Password: `Ksw@0808`
  - Status: ✅ Ready to use

- **INCOIS ERDDAP:**
  - URL: https://erddap.incois.gov.in/erddap/
  - Status: ✅ Public access

---

## 📱 Access Points

Once everything is running:

| Service | URL | Notes |
|---------|-----|-------|
| **API** | http://localhost:8000 | Main backend API |
| **API Docs** | http://localhost:8000/docs | Interactive Swagger UI |
| **MinIO Console** | http://localhost:9001 | Login: minioadmin/minioadmin |
| **PostgreSQL** | localhost:5432 | DB: orca, User: orca, Pass: orca_password |

---

## 🔧 Optional: Start Background Workers

For full functionality, open 2 more terminals:

**Terminal 2 - Celery Worker:**
```cmd
cd C:\Users\SOHAM\Desktop\SIH_2026\backend
venv\Scripts\activate.bat
celery -A app.workers.celery_app worker -l info
```

**Terminal 3 - Celery Beat (Scheduler):**
```cmd
cd C:\Users\SOHAM\Desktop\SIH_2026\backend
venv\Scripts\activate.bat
celery -A app.workers.celery_app beat -l info
```

---

## 🧪 Advanced Testing

### Test Copernicus Marine Adapter

```cmd
# This will test with your real credentials
curl -X POST http://localhost:8000/api/v1/data/latest ^
  -H "Content-Type: application/json" ^
  -d "{\"latitude\": 19.0760, \"longitude\": 72.8777, \"source_id\": \"copernicus_marine\"}"
```

### Test Agent with Live Data

```cmd
curl -X POST http://localhost:8000/api/v1/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"What are the ocean conditions near Mumbai?\", \"mode\": \"live\"}"
```

### Check Freshness Report

```cmd
curl http://localhost:8000/api/v1/freshness/report
```

---

## ❌ Troubleshooting

### Issue: Docker services won't start

```cmd
# Check Docker Desktop is running
docker version

# Stop and restart
docker-compose down
docker-compose up -d postgres redis minio
```

### Issue: Port 8000 already in use

```cmd
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill the process or use a different port
uvicorn app.main:app --reload --port 8001
```

### Issue: Database connection error

```cmd
# Check PostgreSQL is running
docker-compose ps postgres

# View logs
docker-compose logs postgres

# Restart if needed
docker-compose restart postgres
```

### Issue: Module not found errors

```cmd
# Make sure venv is activated
venv\Scripts\activate.bat

# Reinstall dependencies
pip install -r backend/requirements.txt
```

---

## 🎉 Success Checklist

- [ ] Docker containers running (postgres, redis, minio)
- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] Database initialized
- [ ] API server running on port 8000
- [ ] Health endpoint returns "healthy"
- [ ] Swagger docs accessible at /docs
- [ ] Can query data sources
- [ ] Agent responds to chat messages

---

## 🌐 Deploying to Cloud (For Live Link)

To create a live link accessible over the internet, you need to:

### Option 1: Quick Test with Ngrok (Easiest)

1. **Install ngrok:** https://ngrok.com/download
2. **Run ngrok:**
   ```cmd
   ngrok http 8000
   ```
3. **Get public URL:** Copy the https://xxxx.ngrok.io URL
4. **Share link:** Anyone can access your API at that URL

### Option 2: Deploy to Cloud (Production)

**Recommended platforms:**
- **Heroku:** Easy deployment, free tier available
- **AWS EC2/ECS:** Full control, scalable
- **Google Cloud Run:** Serverless, cost-effective
- **Azure App Service:** Good Windows support
- **DigitalOcean:** Simple VPS hosting

**Steps** (general):
1. Push code to GitHub
2. Configure cloud platform
3. Set environment variables (.env values)
4. Deploy containers
5. Configure domain/SSL
6. Update CORS settings in code

---

## 📚 Next Steps

1. **Explore API:** Visit http://localhost:8000/docs and try endpoints
2. **Test with Real Data:** Use your Copernicus/MOSDAC credentials
3. **Read Documentation:** Check `/docs` folder for guides
4. **Add Features:** See `TODO.md` for what to build next
5. **Deploy:** Follow cloud deployment guide for live access

---

## 🆘 Need Help?

1. **Check logs:** API terminal shows all requests
2. **View Docker logs:** `docker-compose logs <service>`
3. **Enable debug:** Set `APP_ENV=development` in `.env`
4. **Check database:** Connect with psql or pgAdmin
5. **Read docs:** See `/docs/DEVELOPMENT.md`

---

## 🎯 Testing Scenarios

### Scenario 1: Check Ocean Conditions
```cmd
curl -X POST http://localhost:8000/api/v1/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"What are current ocean conditions at 19N 72E?\", \"mode\": \"live\"}"
```

### Scenario 2: Find Fishing Zones
```cmd
curl -X POST http://localhost:8000/api/v1/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"Where are good fishing zones near Goa?\", \"mode\": \"live\"}"
```

### Scenario 3: Check Weather
```cmd
curl -X POST http://localhost:8000/api/v1/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"Is it safe to go fishing tomorrow?\", \"mode\": \"standard\"}"
```

---

**🌊 You're all set! ORCA is ready to run! 🌊**

**Start with Step 1 and work through each step. The whole process takes about 10 minutes.**

**Good luck testing! 🚀**
