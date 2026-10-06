# ORCA — Code Audit (Source of Truth)

_Generated: 2026-10-06. Based on reading every file under `backend/app/` and `frontend/`._

## 1. Data Fields — What Is Truly Fetched vs Derived/Synthetic

| Field | Status | Source in Code | Notes |
|-------|--------|----------------|-------|
| **Wave Height** | ✅ Live fetched | Open-Meteo Marine API (`wave_height`) | `live_api.py:163` |
| **Wave Direction** | ✅ Live fetched | Open-Meteo Marine API (`wave_direction`) | |
| **Wave Period** | ✅ Live fetched | Open-Meteo Marine API (`wave_period`) | |
| **Swell Height** | ✅ Live fetched | Open-Meteo Marine API (`swell_wave_height`) | |
| **Wind Speed** | ✅ Live fetched | Open-Meteo Weather API (`wind_speed_10m`) | |
| **Wind Direction** | ✅ Live fetched | Open-Meteo Weather API (`wind_direction_10m`) | |
| **Air Temperature** | ✅ Live fetched | Open-Meteo Weather API (`temperature_2m`) | |
| **Humidity** | ✅ Live fetched | Open-Meteo Weather API (`relative_humidity_2m`) | |
| **Pressure** | ✅ Live fetched | Open-Meteo Weather API (`pressure_msl`) | |
| **SST** | ✅ Live fetched | Open-Meteo Marine API (`sea_surface_temperature`) | |
| **Chlorophyll-a** | ⚠️ Derived | Computed from wave height + coastal proximity heuristic | `live_api.py:363-371`. No satellite data. |
| **Salinity** | ⚠️ Derived | Computed from humidity + latitude heuristic | `live_api.py:374-378`. No oceanographic source. |
| **Ocean Currents** | ✅ Live fetched | Open-Meteo Marine API (`ocean_current_velocity/direction`) | |
| **EEZ Boundaries** | 🔧 Hardcoded | Static polygon in `scientific_engine.py` | India EEZ approximation only. |

## 2. Features — What Is Implemented

| Feature | Status | Location | Notes |
|---------|--------|----------|-------|
| Map with layers (SST, Chl, PFZ, Wind, Sal) | ✅ Working | `frontend/components/map/` | MapLibre GL JS |
| AI Chat Copilot | ✅ Working | `AICopilot.tsx` → `POST /api/chat` → Groq LLM | Groq API key required |
| PFZ zone generation | ✅ Working | `scientific_engine.py:PFZCalculator` | Deterministic from SST/CHL/wave; no ML |
| Deterministic risk engine | ✅ Working | `orchestrator.py:RiskSafetyEngine` | Wave >4m OR wind >60km/h → CRITICAL |
| Hub/Port selector | ✅ Working | `HubSelector.tsx` | Hardcoded list of 10 Indian ports |
| Port analysis with route | ✅ Working | `GET /api/port-analysis` | Requires PostgreSQL (crashes without it) |
| Health check + source pings | ✅ Working | `GET /health`, `GET /api/sources` | Pings INCOIS ERDDAP and Open-Meteo |
| INCOIS ERDDAP SST fetch | ⚠️ Partial | `live_api.py:198-229` | Searches for datasets but returns `None`; falls back |
| Copernicus connector | ❌ Simulated | `copernicus_mosdac_live.py:7-30` | Returns `random.uniform()` — no real fetch |
| MOSDAC connector | ❌ Simulated | `copernicus_mosdac_live.py:33-48` | Returns random values |
| IMD connector | ❌ Skeleton | `imd_weather.py` | Class structure only; no real API calls |
| BHASHINI translation | ❌ Not implemented | — | No code exists |
| Vessel-class thresholds | ✅ Implemented | `safety_thresholds.py` | Configured for 4 vessel types |
| Multilingual UI | ❌ Not implemented | — | English only |
| Voice input/output | ❌ Not implemented | — | No Web Speech API code |
| Audit log | ✅ Implemented | `GET /api/audit` | In-memory decision log tracks verdicts |
| Evidence panel | ✅ Implemented | `frontend/components/copilot/AICopilot.tsx` | Included in Chat responses |
| Multi-agent system | ✅ Implemented | `orchestrator.py` & `agents/` | 10 custom python agents working sequentially |

## 3. Architecture Reality

The backend is a **single FastAPI application** (`app/main.py`) with:
- `live_api.py` — all HTTP endpoints (health, sources, observations, PFZ, chat, recommendations, ports, port-analysis)
- `services/orchestrator.py` — Coordinates 10 custom agents in sequence, passes context, manages evidence.
- `services/scientific_engine.py` — deterministic PFZ calculator with SST gradient, thermal front, and species habitat logic
- `agents/` — Implementation of 10 real agent classes (e.g., PlannerAgent, OceanAgent, RiskAgent) with health checks.

There is **no LangGraph** and **no Redis/Celery task queue** in the live path, but the system IS multi-agent using sequential function calls.

## 4. Database Dependency

The app imports `AsyncSessionLocal` from `app.core.database` which requires a PostgreSQL connection string. Several endpoints (`/api/pfz`, `/api/ports`, `/api/port-analysis`) will crash if PostgreSQL is unavailable. The chat endpoint has a 2-second timeout fallback.
