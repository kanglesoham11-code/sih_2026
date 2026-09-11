# ORCA Development Guide

This document provides comprehensive guidance for developers working on the ORCA platform.

## Project Structure

```
SIH_2026/
├── backend/              # Python FastAPI backend
│   ├── alembic/         # Database migrations
│   ├── app/
│   │   ├── agents/      # Multi-agent system
│   │   ├── api/         # REST API endpoints
│   │   ├── connectors/  # Source adapters
│   │   ├── core/        # Configuration, database, logging
│   │   ├── models/      # SQLAlchemy database models
│   │   ├── schemas/     # Pydantic request/response schemas
│   │   ├── services/    # Business logic (gateway, freshness)
│   │   ├── utils/       # Utility functions
│   │   └── workers/     # Celery background tasks
│   ├── tests/           # Test suite
│   ├── requirements.txt # Python dependencies
│   └── Dockerfile       # Backend container
├── frontend/            # Next.js frontend (to be implemented)
├── docs/                # Documentation
├── scripts/             # Utility scripts
├── monitoring/          # Prometheus, Grafana configs
└── docker-compose.yml   # Local development stack
```

## Development Setup

### 1. Prerequisites

- Python 3.12+
- Docker Desktop
- Git
- VS Code (recommended) or your preferred IDE

### 2. Clone and Setup

```bash
# Clone repository
git clone <repository-url>
cd SIH_2026

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt  # If exists
```

### 3. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# CRITICAL: Never commit .env to Git
```

### 4. Start Infrastructure Services

```bash
# Start PostgreSQL, Redis, MinIO
docker-compose up -d postgres redis minio

# Wait for services to be ready (~30 seconds)
docker-compose logs -f postgres  # Check logs
```

### 5. Initialize Database

```bash
# Run migrations
alembic upgrade head

# Optional: Load seed data
python scripts/seed_sources.py
```

### 6. Start Development Server

```bash
# Start FastAPI server
uvicorn app.main:app --reload --port 8000

# In another terminal, start Celery worker
celery -A app.workers.celery_app worker -l info

# In another terminal, start Celery beat (scheduler)
celery -A app.workers.celery_app beat -l info
```

## Architecture Overview

### Multi-Agent System (PRD Section 13)

ORCA uses a collaborative multi-agent architecture:

1. **Conversation Agent**: Intent classification, NLU, response synthesis
2. **Planner Agent**: Task decomposition, STANDARD vs LIVE mode determination
3. **Domain Agents**:
   - PFZ Intelligence Agent
   - Ocean Intelligence Agent
   - Weather Intelligence Agent
   - Geospatial Agent
   - Risk Assessment Agent
   - Route Optimization Agent

### Data Gateway (PRD Section 4.1)

The gateway wraps all source adapters with:
- **Rate limiting**: Token bucket algorithm using Redis
- **Circuit breakers**: Prevent cascading failures
- **Retry logic**: Exponential backoff
- **Provenance capture**: Store raw responses in MinIO

### Freshness Management (PRD Section 9)

Tracks data age and enforces freshness policies:
- **CRITICAL**: 5 minutes (NRT data)
- **HIGH**: 15 minutes (forecasts)
- **MEDIUM**: 1 hour (daily aggregates)
- **LOW**: 24 hours (climatology)

## Adding a New Data Source

### Step 1: Create Adapter

```python
# backend/app/connectors/my_source.py

from app.connectors.base import (
    SourceAdapter,
    SourceMetadata,
    Payload,
    HealthStatus,
    SpatialQuery,
    AcquisitionMode,
    DataType,
)

class MySourceAdapter(SourceAdapter):
    SOURCE_ID = "my_source"
    
    def __init__(self):
        super().__init__(timeout=10)
        self.client = httpx.AsyncClient()
    
    def get_metadata(self) -> SourceMetadata:
        return SourceMetadata(
            source_id=self.SOURCE_ID,
            provider="Provider Name",
            name="Source Name",
            interface_type=AcquisitionMode.REST_API,
            base_url="https://api.example.com",
            endpoint_verified=True,
            auth_required=False,
            capabilities=["health_check", "get_latest"],
            variables=["temperature", "salinity"],
            coverage="Indian Ocean",
        )
    
    async def health_check(self) -> HealthStatus:
        # Implement health check
        pass
    
    async def get_latest(self, q: SpatialQuery) -> Payload:
        # Implement data retrieval
        pass
```

### Step 2: Register in Gateway

```python
# backend/app/main.py or initialization module

from app.services.gateway import DataGateway
from app.connectors.my_source import MySourceAdapter

@app.on_event("startup")
async def startup_event():
    gateway = DataGateway(redis_client, minio_client)
    
    # Register adapter
    my_adapter = MySourceAdapter()
    gateway.register_adapter(my_adapter)
```

### Step 3: Configure Rate Limits

```python
# backend/app/services/gateway.py

self.rate_limits = {
    "my_source": {"max_tokens": 60, "refill_rate": 2.0},
    # ...
}
```

### Step 4: Add Credentials

```bash
# .env.example and .env
MY_SOURCE_API_KEY=your_key_here
MY_SOURCE_BASE_URL=https://api.example.com
```

```python
# backend/app/core/config.py

class Settings(BaseSettings):
    MY_SOURCE_API_KEY: Optional[str] = None
    MY_SOURCE_BASE_URL: str = "https://api.example.com"
```

## Testing

### Unit Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_gateway.py

# Run specific test
pytest tests/test_gateway.py::test_rate_limiting
```

### Integration Tests

```bash
# Start test database
docker-compose -f docker-compose.test.yml up -d

# Run integration tests
pytest tests/integration/

# Cleanup
docker-compose -f docker-compose.test.yml down -v
```

### Manual Testing

```bash
# Test API endpoints
curl http://localhost:8000/health

# Test agent query
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the current wave conditions near Mumbai?"}'
```

## Database Migrations

### Create Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new table"

# Create empty migration
alembic revision -m "Custom migration"
```

### Apply Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade to specific revision
alembic upgrade <revision_id>

# Downgrade one revision
alembic downgrade -1

# Show current revision
alembic current

# Show migration history
alembic history
```

## Code Quality

### Formatting

```bash
# Format with Black
black backend/app

# Check without applying
black --check backend/app
```

### Linting

```bash
# Lint with Ruff
ruff check backend/app

# Auto-fix issues
ruff check --fix backend/app
```

### Type Checking

```bash
# Check types with mypy
mypy backend/app
```

### Security Audit

```bash
# Audit dependencies
pip-audit

# Check for secrets in code
# (Use tools like trufflehog, gitleaks)
```

## Debugging

### FastAPI Debug Mode

```python
# backend/app/main.py
app = FastAPI(debug=True)  # Enable debug mode
```

### Celery Debug

```bash
# Run worker with debug logging
celery -A app.workers.celery_app worker --loglevel=debug

# Run single task synchronously
celery -A app.workers.celery_app call app.workers.tasks.refresh_source_task --args='["incois_erddap"]'
```

### Database Queries

```bash
# Connect to database
docker-compose exec postgres psql -U orca -d orca

# View tables
\dt

# View schema
\d+ sources

# Query data
SELECT * FROM sources;
```

## Performance Optimization

### Database Optimization

- Add indexes on frequently queried columns
- Use database connection pooling
- Implement query result caching
- Use EXPLAIN ANALYZE for slow queries

### API Optimization

- Enable response compression (GZip)
- Implement Redis caching for expensive operations
- Use async/await for I/O operations
- Batch database queries

### Background Task Optimization

- Use Celery routing for task prioritization
- Implement task retries with exponential backoff
- Monitor task execution time
- Use task result expiration

## Deployment

### Production Checklist

- [ ] Set `APP_ENV=production`
- [ ] Use strong secret keys
- [ ] Enable HTTPS
- [ ] Configure CORS properly
- [ ] Set up monitoring (Sentry, Prometheus)
- [ ] Configure log aggregation
- [ ] Set up automated backups
- [ ] Configure rate limiting
- [ ] Enable security headers
- [ ] Test disaster recovery

### Docker Deployment

```bash
# Build images
docker-compose build

# Start production stack
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f backend

# Scale workers
docker-compose up -d --scale worker=4
```

## Troubleshooting

### Common Issues

**Issue: Database connection errors**
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Verify DATABASE_URL in .env
```

**Issue: Celery worker not picking up tasks**
```bash
# Check Redis connection
redis-cli -h localhost -p 6379 ping

# Check Celery broker URL
echo $REDIS_URL

# Restart workers
docker-compose restart worker
```

**Issue: Source adapter timeouts**
```bash
# Check source health
curl http://localhost:8000/api/v1/health

# Increase timeout in adapter
super().__init__(timeout=30)

# Check circuit breaker status
# (View in logs or admin dashboard)
```

## Contributing

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes
3. Run tests: `pytest`
4. Run linters: `black . && ruff check .`
5. Commit with descriptive message
6. Push and create pull request
7. Wait for review and CI checks

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [PostGIS Documentation](https://postgis.net/documentation/)
- [ORCA PRD](../PRD.md)
- [Architecture Docs](./architecture.md)
