## ORCA Quick Start Guide

Get ORCA running on your local machine in under 10 minutes.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.12+** installed
- **Docker Desktop** running
- **Git** installed
- At least 8GB RAM available
- 10GB free disk space

## Step 1: Clone Repository

```bash
git clone <repository-url>
cd SIH_2026
```

## Step 2: Environment Setup

### Windows

```cmd
# Copy environment template
copy .env.example .env

# Edit .env with your credentials
notepad .env
```

### Linux/Mac

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

### Required Configuration

At minimum, configure these in `.env`:

```bash
# Application secrets
APP_SECRET_KEY=generate-a-random-secret-key
JWT_SECRET_KEY=generate-another-random-secret-key

# Database
DATABASE_URL=postgresql+asyncpg://orca:orca_password@localhost:5432/orca

# Redis
REDIS_URL=redis://localhost:6379/0

# MinIO
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# LLM (OpenAI)
OPENAI_API_KEY=your-openai-api-key-here
```

> **Security Note:** In production, use strong random keys. Generate with:
> ```bash
> python -c "import secrets; print(secrets.token_urlsafe(32))"
> ```

## Step 3: Start Infrastructure

Start PostgreSQL, Redis, and MinIO using Docker Compose:

```bash
docker-compose up -d postgres redis minio
```

Wait ~30 seconds for services to initialize.

### Verify Services

```bash
# Check if services are running
docker-compose ps

# You should see:
# - postgres (port 5432)
# - redis (port 6379)
# - minio (port 9000, 9001)
```

## Step 4: Setup Python Environment

### Windows

```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate.bat

# Install dependencies
cd backend
pip install -r requirements.txt
```

### Linux/Mac

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt
```

## Step 5: Initialize Database

```bash
# Run migrations
alembic upgrade head

# Seed initial data
python scripts/init_database.py
```

You should see:
```
✅ Database tables created
✅ Data sources seeded
✅ Marine boundaries seeded
```

## Step 6: Start ORCA Services

### Option A: Using Startup Script (Recommended)

#### Windows
```cmd
cd ..
scripts\start_dev.bat
```

#### Linux/Mac
```bash
cd ..
chmod +x scripts/start_dev.sh
./scripts/start_dev.sh
```

### Option B: Manual Start

Open 3 terminal windows:

**Terminal 1 - API Server:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Celery Worker:**
```bash
cd backend
celery -A app.workers.celery_app worker -l info
```

**Terminal 3 - Celery Beat:**
```bash
cd backend
celery -A app.workers.celery_app beat -l info
```

## Step 7: Verify Installation

### Check API Health

Open your browser: http://localhost:8000/health

You should see:
```json
{
  "status": "healthy",
  "environment": "development",
  "version": "1.0.0"
}
```

### Check API Documentation

Open: http://localhost:8000/docs

You should see the interactive Swagger UI.

### Test Agent Chat

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! What can you help me with?",
    "mode": "standard"
  }'
```

## Step 8: Access Services

ORCA services are now running:

| Service | URL | Credentials |
|---------|-----|-------------|
| API | http://localhost:8000 | - |
| API Docs | http://localhost:8000/docs | - |
| MinIO Console | http://localhost:9001 | minioadmin / minioadmin |
| PostgreSQL | localhost:5432 | orca / orca_password |
| Redis | localhost:6379 | - |

## Common Issues

### Issue: Database connection error

**Solution:** Check if PostgreSQL is running
```bash
docker-compose ps postgres
docker-compose logs postgres
```

### Issue: Redis connection error

**Solution:** Check if Redis is running
```bash
docker-compose ps redis
docker-compose logs redis
```

### Issue: "alembic: command not found"

**Solution:** Ensure virtual environment is activated and dependencies are installed
```bash
# Activate venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate.bat # Windows

# Reinstall dependencies
cd backend
pip install -r requirements.txt
```

### Issue: Port already in use

**Solution:** Change port or stop conflicting service
```bash
# Check what's using port 8000
# Windows:
netstat -ano | findstr :8000

# Linux/Mac:
lsof -i :8000
```

### Issue: MinIO buckets not created

**Solution:** Create buckets manually
1. Open http://localhost:9001
2. Login with minioadmin/minioadmin
3. Create buckets: `orca-raw`, `orca-processed`

## Next Steps

Now that ORCA is running:

1. **Explore the API**
   - Visit http://localhost:8000/docs
   - Try different endpoints
   - Check response schemas

2. **Test Agent Interactions**
   ```bash
   # Ask about fishing zones
   curl -X POST http://localhost:8000/api/v1/chat \
     -H "Content-Type: application/json" \
     -d '{
       "message": "What are good fishing zones near Mumbai?",
       "mode": "live"
     }'
   ```

3. **Configure Data Sources**
   - Add API keys for IMD, Copernicus, etc. in `.env`
   - Test source connections
   - View freshness report

4. **Read Documentation**
   - [Architecture](./architecture.md)
   - [Development Guide](./DEVELOPMENT.md)
   - [API Reference](./API.md)

5. **Start Development**
   - Read [DEVELOPMENT.md](./DEVELOPMENT.md) for guidelines
   - Check [PROJECT_STATUS.md](../PROJECT_STATUS.md) for pending work
   - Look for TODOs in the code

## Development Workflow

### Making Changes

1. Edit code in `backend/app/`
2. API auto-reloads (thanks to `--reload` flag)
3. Test changes in browser or with curl
4. Check logs in terminal

### Database Changes

1. Edit models in `backend/app/models/`
2. Generate migration:
   ```bash
   alembic revision --autogenerate -m "Description"
   ```
3. Review migration in `backend/alembic/versions/`
4. Apply migration:
   ```bash
   alembic upgrade head
   ```

### Adding a New Endpoint

1. Add schema in `backend/app/schemas/`
2. Add endpoint in `backend/app/api/endpoints.py`
3. Test at http://localhost:8000/docs
4. Add to `docs/API.md`

## Stopping Services

### Stop ORCA

Press `Ctrl+C` in all terminal windows

### Stop Infrastructure

```bash
docker-compose down
```

### Stop and Remove Data

```bash
# WARNING: This deletes all data!
docker-compose down -v
```

## Getting Help

- **Check Logs:**
  - API: Terminal running uvicorn
  - Worker: Terminal running celery worker
  - PostgreSQL: `docker-compose logs postgres`
  - Redis: `docker-compose logs redis`

- **Documentation:**
  - [Architecture](./architecture.md)
  - [Development Guide](./DEVELOPMENT.md)
  - [API Reference](./API.md)

- **Debugging:**
  - Enable debug mode in `.env`: `APP_ENV=development`
  - Check `backend/logs/` for detailed logs
  - Use `--loglevel=debug` for celery

## Troubleshooting Checklist

Before asking for help, check:

- [ ] All services running: `docker-compose ps`
- [ ] Virtual environment activated: `which python` should show venv
- [ ] Dependencies installed: `pip list | grep fastapi`
- [ ] Database initialized: `alembic current`
- [ ] `.env` file configured with valid credentials
- [ ] Ports 8000, 5432, 6379, 9000 not in use
- [ ] At least 8GB RAM available
- [ ] Docker Desktop running and healthy

## Success!

If you see the API running at http://localhost:8000 and can access /docs, congratulations! You've successfully set up ORCA. 🎉

Start exploring, building, and contributing!
