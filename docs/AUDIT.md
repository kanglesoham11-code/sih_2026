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
| **SST** | ⚠️ Derived | Air temp + 1.5°C + hash jitter | `live_api.py:361`. NOT fetched from any ocean SST dataset. |
| **Chlorophyll-a** | ⚠️ Derived | Computed from wave height + coastal proximity heuristic | `live_api.py:363-371`. No satellite data. |
| **Salinity** | ⚠️ Derived | Computed from humidity + latitude heuristic | `live_api.py:374-378`. No oceanographic source. |
| **Ocean Currents** | ⚠️ Derived | Estimated from wind via Ekman transport formula | In `scientific_engine.py`. No current-meter or model data. |
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
| Vessel-class thresholds | ❌ Not implemented | — | Single threshold for all vessel types |
| Multilingual UI | ❌ Not implemented | — | English only |
| Voice input/output | ❌ Not implemented | — | No Web Speech API code |
| Audit log | ❌ Not implemented | — | No decision logging |
| Evidence panel | ❌ Not implemented | — | No evidence[] in API responses |
| Multi-agent system | ❌ Not implemented | — | Single `orchestrate_chat()` function |

## 3. Architecture Reality

The backend is a **single FastAPI application** (`app/main.py`) with:
- `live_api.py` — all HTTP endpoints (health, sources, observations, PFZ, chat, recommendations, ports, port-analysis)
- `services/orchestrator.py` — one function `orchestrate_chat()` that fetches Open-Meteo data, computes PFZ, formats context, and passes to LLM
- `services/scientific_engine.py` — deterministic PFZ calculator with SST gradient, thermal front, and species habitat logic
- `connectors/` — skeleton connectors for INCOIS, IMD, Copernicus, MOSDAC (none truly functional)

There is **no LangGraph**, **no multi-agent orchestration**, **no agent trace**, and **no Redis/Celery task queue** in the live path.

## 4. Database Dependency

The app imports `AsyncSessionLocal` from `app.core.database` which requires a PostgreSQL connection string. Several endpoints (`/api/pfz`, `/api/ports`, `/api/port-analysis`) will crash if PostgreSQL is unavailable. The chat endpoint has a 2-second timeout fallback.
