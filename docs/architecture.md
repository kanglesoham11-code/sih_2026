# ORCA Architecture

## Overview

ORCA is a **LIVE DATA INTELLIGENCE PLATFORM** for marine intelligence, not a static dataset repository. The system continuously acquires current information from official machine-readable sources through APIs, ERDDAP services, and official SDKs.

## Core Principle

> **"ORCA continuously acquires live data through the best available authoritative machine-readable interface, with API/service access first and compliant scraping only as a last resort."**

## Architecture Diagram

```
USER (web / mobile)
    │
    ▼
┌─────────────────────────────────┐
│ Conversation & Language Agent   │  Language detect, translation
└────────────┬────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│ Intent + Location + Time        │  Geocode, time window extraction
│ Understanding                   │
└────────────┬────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│ Planner Agent                   │  Task graph, STANDARD vs LIVE mode
└────────────┬────────────────────┘
    │ (tool calls - never raw HTTP from LLM)
    ▼
┌─────────────────────────────────┐
│ ORCA DATA GATEWAY /             │  Source adapters, auth, rate limits
│ LIVE DATA BROKER                │  retries, circuit breakers
└────────────┬────────────────────┘
    │
    ▼
[INCOIS] [IMD] [Copernicus] [MOSDAC] [GFW] [OBIS] [ISRO] [Others]
    │
    ▼
┌─────────────────────────────────┐
│ Normalization + Validation      │  Canonical schema, units, CRS
└────────────┬────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│ Freshness Manager               │  Source-driven staleness marking
└────────────┬────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│ Redis Cache | PostgreSQL/PostGIS│  Hot cache + persistent storage
│ MinIO/S3 Raw Store              │
└────────────┬────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│ Spatial / Temporal Fusion       │  Grid align, interpolation
└────────────┬────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│ Specialized Agents              │  PFZ, Ocean, Weather, Geo, Risk
└────────────┬────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│ Risk + Route + Evidence         │  Decision support assembly
└────────────┬────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│ Visualization / Map / Charts    │  Frontend rendering
└─────────────────────────────────┘
```

## Key Components

### 1. Data Gateway Layer
- **Responsibility**: Single choke point for all external data acquisition
- **Features**: 
  - Source adapter registration
  - Per-provider rate limiting (Redis-backed)
  - Circuit breakers for fault tolerance
  - Retry with exponential backoff
  - Provenance capture (raw → MinIO)
  - Parallel fan-out for multi-source queries

### 2. Source Adapters
Four acquisition modes (strict preference order):
1. **Mode A** - Direct REST API
2. **Mode B** - Scientific data service (ERDDAP, OGC, STAC)
3. **Mode C** - Official SDK/data client
4. **Mode D** - Compliant scraping (last resort only)

### 3. Freshness Engine
- Source-driven freshness algorithm
- Cache policies per data type (CRITICAL/HIGH/MEDIUM/LOW/STATIC)
- Automatic staleness detection
- STANDARD vs LIVE query modes

### 4. Agent System
Specialized agents with tool-only data access:
- **Planner Agent**: Task decomposition, mode selection
- **PFZ/Fishing Intelligence Agent**: Fishing zone analysis
- **Ocean Intelligence Agent**: Waves, currents, SST
- **Weather Intelligence Agent**: IMD warnings, forecasts
- **Geospatial Agent**: EEZ, protected areas, geofencing
- **Risk Assessment Agent**: Hazard scoring, candidate filtering
- **Route Optimization Agent**: Safe path planning
- **Evidence Agent**: Provenance assembly

### 5. Storage Tiers
- **Hot Cache (Redis)**: Latest values, freshness metadata
- **Operational DB (PostgreSQL + PostGIS)**: Canonical data, geometries
- **Raw Store (MinIO/S3)**: Original API responses, NetCDF files

## Data Flow

### Normal Query (STANDARD Mode)
1. User query → Language detection → Intent extraction
2. Planner checks cache freshness
3. If fresh: return cached data with timestamps
4. If stale: Gateway fetches from source → Normalize → Cache → Return

### Critical Query (LIVE Mode)
1. Triggers: "right now", "current", safety questions, next N hours
2. Bypass cache entirely
3. Force refresh from authoritative sources
4. Verify source timestamps
5. Cross-check multiple sources
6. Lower confidence on disagreement

## Non-Negotiable Requirements

1. **API-first architecture** - ERDDAP is access layer, not dataset
2. **Live/NRT/forecast strictly separated** from historical data
3. **Source timestamp tracking** - Every value has source_updated_at
4. **Demand-driven retrieval** - Normal queries use cache
5. **Forced refresh** - Safety queries get fresh data
6. **Parallel execution** - Independent sources queried simultaneously
7. **No secrets in code** - Environment variables only
8. **Never invent endpoints** - Undocumented = "verification required"
9. **Traceable recommendations** - Full provenance chain
10. **Decision support only** - NOT official safety clearance

## Security

- Secrets manager for production (Vault/AWS/GCP)
- Environment variables for development
- SSRF protection (domain allowlist)
- TLS everywhere
- RBAC (user/researcher/admin)
- Audit logging
- Rate limiting per user/IP

## Scalability

- Stateless API servers (horizontal scaling)
- Redis cluster for cache
- PostgreSQL read replicas
- MinIO distributed mode
- Celery workers (CPU-bound tasks)
- Async I/O throughout

## Observability

- Prometheus metrics
- Grafana dashboards (user + ops)
- OpenTelemetry traces
- Structured JSON logging
- Source health monitoring
- Freshness tracking per source

## See Also

- [Data Sources](data-sources.md)
- [API Documentation](api.md)
- [Deployment Guide](deployment.md)
- [Security](security.md)
