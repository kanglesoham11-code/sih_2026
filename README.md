<p align="center">
  <img src="https://img.shields.io/badge/ORCA-Marine%20Intelligence-0ea5e9?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiPjxwYXRoIGQ9Ik0yIDEyaDIwIi8+PHBhdGggZD0iTTEyIDJhMTUuMyAxNS4zIDAgMCAxIDQgMTAgMTUuMyAxNS4zIDAgMCAxLTQgMTAgMTUuMyAxNS4zIDAgMCAxLTQtMTAgMTUuMyAxNS4zIDAgMCAxIDQtMTB6Ii8+PC9zdmc+" alt="ORCA Badge"/>
</p>

<h1 align="center">🐋 ORCA — Ocean Reconnaissance & Catch Advisory</h1>

<p align="center">
  <b>AI-Powered Marine Intelligence Platform for Indian Fishermen</b><br/>
  Smart Innovation Hackathon (SIH) 2026
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Next.js-14-black?logo=next.js" alt="Next.js"/>
  <img src="https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/MapLibre-4.7-blue?logo=mapbox" alt="MapLibre"/>
  <img src="https://img.shields.io/badge/PostgreSQL-PostGIS-336791?logo=postgresql" alt="PostgreSQL"/>
  <img src="https://img.shields.io/badge/Groq-LLM-orange" alt="Groq"/>
</p>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Workflow Pipeline](#-workflow-pipeline)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [Scientific Engine](#-scientific-engine)
- [API Reference](#-api-reference)
- [Indian EEZ Boundary Enforcement](#-indian-eez-boundary-enforcement)
- [Screenshots](#-screenshots)
- [Team](#-team)

---

## 🌊 Overview

**ORCA** is an intelligent marine advisory system that helps Indian fishermen find the **best fishing zones** using real-time oceanographic data, satellite-grade scientific calculations, and an AI chatbot — all within **India's international maritime boundaries**.

The system combines **live weather/ocean data** from Open-Meteo, Copernicus, MOSDAC, and INCOIS with a **deterministic scientific engine** (based on the ORCA Scientific Rulebook) to compute Potential Fishing Zones (PFZ), then presents results through a conversational AI interface connected to an interactive map.

> **The fisherman asks a simple question. ORCA does all the science and gives a clear answer.**

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI Copilot Chatbot** | Natural language interface — ask "Where should I fish?" and get actionable advice |
| 🗺️ **Interactive Ocean Map** | MapLibre-powered map with real-time ocean data layers (SST, Chlorophyll, Salinity, Waves, Wind) |
| 🎯 **PFZ Zone Detection** | Scientific computation of Potential Fishing Zones using INCOIS methodology |
| 🛣️ **Sea-Only Route Planning** | Water-only navigation paths from any Mumbai port to the best fishing zone |
| 🛡️ **Safety Override System** | IMD-grade safety checks — dangerous conditions override all fishing recommendations |
| 🇮🇳 **Indian EEZ Enforcement** | All fishing zones strictly within India's international maritime boundaries |
| 📡 **Live Data Integration** | Real-time SST, wave height, wind speed, chlorophyll from Open-Meteo marine API |
| 🔬 **Deterministic Science** | All calculations follow the ORCA Scientific Rulebook — LLM never invents data |
| 🏗️ **Land Masking** | Ocean data layers only render over water — land areas are transparent |
| ⚓ **Multi-Port Support** | 9 Mumbai ports with port-specific water-channel routing |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ORCA ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    FRONTEND (Next.js 14)                      │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │  │
│  │  │ MainMap  │  │AICopilot │  │InfoPanel │  │ StatusBar    │  │  │
│  │  │(MapLibre)│  │(Chatbot) │  │(Details) │  │(Live Status) │  │  │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────────────┘  │  │
│  │       │              │              │                          │  │
│  │  ┌────┴──────────────┴──────────────┴─────────────────────┐   │  │
│  │  │              Zustand Global State Store                │   │  │
│  │  │  (map state, layers, routes, PFZ zones, chat history)  │   │  │
│  │  └────────────────────────┬───────────────────────────────┘   │  │
│  └───────────────────────────┼───────────────────────────────────┘  │
│                              │ HTTP/REST                            │
│  ┌───────────────────────────┼───────────────────────────────────┐  │
│  │                  BACKEND (FastAPI + Uvicorn)                   │  │
│  │                           │                                    │  │
│  │  ┌────────────────────────┴────────────────────────────────┐  │  │
│  │  │               ORCHESTRATOR (orchestrator.py)             │  │  │
│  │  │  Intent Detection → Data Fetch → Science → LLM → Map    │  │  │
│  │  └──┬──────────┬──────────┬──────────┬──────────┬──────────┘  │  │
│  │     │          │          │          │          │              │  │
│  │  ┌──┴──┐  ┌───┴───┐  ┌──┴───┐  ┌──┴──┐  ┌───┴────┐        │  │
│  │  │Live │  │Science│  │ EEZ  │  │Groq │  │ Risk   │        │  │
│  │  │Data │  │Engine │  │Check │  │ LLM │  │Safety  │        │  │
│  │  │Fetch│  │(ORCA  │  │(India│  │(NLP │  │Engine  │        │  │
│  │  │     │  │Rules) │  │EEZ)  │  │Layer│  │        │        │  │
│  │  └──┬──┘  └───┬───┘  └──┬───┘  └──┬──┘  └───┬────┘        │  │
│  │     │         │         │         │          │              │  │
│  └─────┼─────────┼─────────┼─────────┼──────────┼──────────────┘  │
│        │         │         │         │          │                  │
│  ┌─────┴─────────┴─────────┴─────────┴──────────┴──────────────┐  │
│  │                    EXTERNAL DATA SOURCES                     │  │
│  │  Open-Meteo Marine API  │  Copernicus  │  MOSDAC  │  INCOIS  │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                    DATA PERSISTENCE                          │  │
│  │     PostgreSQL + PostGIS     │     Redis Cache               │  │
│  └─────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Workflow Pipeline

### End-to-End: User Question → Map Visualization

```mermaid
flowchart TD
    A["🧑 Fisherman asks:\n'Where should I fish today?'"] --> B["🤖 AI Copilot\n(AICopilot.tsx)"]
    B --> C["📡 Backend API\n/api/v1/chat"]
    C --> D["🧠 Orchestrator\n(Intent Detection)"]
    
    D --> E{"Intent?"}
    E -->|fishing/navigation| F["📊 Live Data Fetch\n(Open-Meteo Marine API)"]
    E -->|weather| G["🌤️ Weather Context"]
    E -->|safety| H["⚠️ Risk Assessment"]
    
    F --> I["🔬 Scientific Engine\n(ORCA Rulebook)"]
    
    I --> I1["SST Gradient\n|∇SST| = √(∂SST/∂x² + ∂SST/∂y²)"]
    I --> I2["Chlorophyll Front\nlog₁₀(CHL) gradient"]
    I --> I3["Fishing Suitability\nSST·0.35 + CHL·0.40 + Front + Current"]
    I --> I4["Safety Override\nWave > 4m → Score = 0"]
    
    I1 & I2 & I3 & I4 --> J["🇮🇳 EEZ Boundary Check\n(Point-in-Polygon)"]
    
    J -->|Inside Indian Waters| K["✅ Valid PFZ Zones\n(Top 5 by score)"]
    J -->|Outside Border| L["❌ Rejected"]
    
    K --> M["🗣️ Groq LLM\n(Explain results simply)"]
    M --> N["📋 Map Actions\n(route_to_pfz, show_zones,\nhighlight_pfz, fly_to)"]
    
    N --> O["🗺️ Frontend Map\n(MapLibre GL)"]
    O --> P["🎯 PFZ Zones Rendered\n+ Sea Route Drawn\n+ Camera Flies To Area"]
    
    style A fill:#0ea5e9,color:white
    style I fill:#8b5cf6,color:white
    style J fill:#f59e0b,color:white
    style K fill:#22c55e,color:white
    style L fill:#ef4444,color:white
    style P fill:#0ea5e9,color:white
```

### Detailed Scientific Pipeline

```
User Query
    │
    ▼
┌──────────────────────────────────────────────────────────────┐
│ 1. INTENT DETECTION                                          │
│    Keywords → fishing | navigation | weather | safety        │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. LIVE DATA ACQUISITION                                     │
│    Open-Meteo Marine API → SST, Wave Height, Wind Speed      │
│    Open-Meteo Weather API → Air Temp, Wind Direction         │
│    (Copernicus/MOSDAC for production deployment)             │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ 3. SCIENTIFIC ENGINE (Deterministic — No AI Guessing)        │
│                                                              │
│    ┌─────────────────┐  ┌──────────────────┐                │
│    │ SST Gradient     │  │ Chlorophyll Front │                │
│    │ (Rulebook §2-3)  │  │ (Rulebook §4-5)  │                │
│    └────────┬─────────┘  └────────┬─────────┘                │
│             │                     │                          │
│    ┌────────┴─────────────────────┴─────────┐                │
│    │      Fishing Suitability Model          │                │
│    │      (Rulebook §16-17)                  │                │
│    │                                         │                │
│    │  Score = SST_score × 0.35               │                │
│    │       + CHL_score × 0.40                │                │
│    │       + Front_bonus                     │                │
│    │       + Current_bonus                   │                │
│    │                                         │                │
│    │  Safety Override:                       │                │
│    │    Wave > 4m  → Score = 0 (UNSAFE)      │                │
│    │    Wind > 50  → Score = 0 (GALE)        │                │
│    └────────┬────────────────────────────────┘                │
│             │                                                │
│    ┌────────┴────────────────────────────────┐                │
│    │      India EEZ Boundary Filter          │                │
│    │      (Ray-casting point-in-polygon)      │                │
│    │      Only zones inside Indian waters     │                │
│    └────────┬────────────────────────────────┘                │
│             │                                                │
│    ┌────────┴────────────────────────────────┐                │
│    │      PFZ Zone Ranking                   │                │
│    │      Sort by score → Return top 5       │                │
│    └─────────────────────────────────────────┘                │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ 4. LLM EXPLANATION LAYER (Groq)                              │
│    Takes computed PFZ data + weather context                 │
│    Generates SIMPLE, non-technical explanation               │
│    "Go 15km southwest — best fishing area today"             │
│    LLM NEVER invents coordinates or readings                 │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ 5. MAP ACTIONS → FRONTEND                                    │
│    • fly_to: Camera animates to fishing area                 │
│    • show_pfz_zones: Render all 5 PFZ polygons on map       │
│    • route_to_pfz: Draw sea-only route from port to best PFZ│
│    • highlight_pfz: Highlight the #1 recommended zone        │
└──────────────────────────────────────────────────────────────┘
```

### Sea Route Generation

```
Port Location → Classify Port → Select Water Waypoints → Interpolate → Render

EAST-SIDE PORTS (Sassoon Dock, Gateway, Bhaucha Dhakka):
  Port → Harbor Channel South → South of Colaba (open sea) → Open Sea SW → PFZ

WEST-SIDE PORTS (Marine Drive, Worli):
  Port → Straight West to Open Sea → PFZ

NORTH PORTS (Juhu, Bhati):
  Port → West to Open Sea → PFZ

Every interpolated point is verified to be over water.
```

---

## 🛠️ Tech Stack

### Frontend
| Technology | Version | Purpose |
|-----------|---------|---------|
| Next.js | 14.2 | React framework with SSR |
| React | 18.3 | UI library |
| MapLibre GL | 4.7 | Open-source map rendering |
| react-map-gl | 7.1 | React bindings for MapLibre |
| Zustand | 4.5 | Global state management |
| TanStack Query | 5.56 | Server state & data fetching |
| Framer Motion | 11.5 | Animations & transitions |
| Recharts | 2.12 | Data visualization charts |
| Lucide React | 0.441 | Icon library |

### Backend
| Technology | Version | Purpose |
|-----------|---------|---------|
| FastAPI | 0.109 | Async REST API framework |
| Uvicorn | 0.27 | ASGI server |
| Groq SDK | 0.11 | LLM inference (Llama 3) |
| SQLAlchemy | 2.0 | ORM + async database |
| GeoAlchemy2 | 0.14 | PostGIS spatial queries |
| HTTPX | 0.26 | Async HTTP client |
| NumPy | 1.26 | Scientific computation |
| xarray | 2024.1 | Multidimensional ocean data |
| Shapely | 2.0 | Geometric operations |

### Infrastructure
| Technology | Purpose |
|-----------|---------|
| PostgreSQL + PostGIS | Spatial database for zones, ports, geospatial queries |
| Redis | Caching layer for API responses |
| Docker Compose | Container orchestration |
| OpenStreetMap | Base map tiles |

---

## 📁 Project Structure

```
SIH_2026/
├── 📂 backend/                        # Python FastAPI Backend
│   ├── 📂 app/
│   │   ├── 📂 api/                    # REST API endpoints
│   │   │   └── v1/
│   │   │       ├── chat.py            # /api/v1/chat — AI copilot endpoint
│   │   │       ├── observations.py    # /api/v1/observations — ocean data
│   │   │       ├── fishing_hubs.py    # /api/v1/fishing-hubs — port data
│   │   │       ├── pfz_zones.py       # /api/v1/pfz-zones — PFZ data
│   │   │       └── warnings.py        # /api/v1/warnings — safety alerts
│   │   ├── 📂 core/                   # Configuration & setup
│   │   │   ├── config.py              # Environment configuration
│   │   │   ├── database.py            # PostgreSQL + PostGIS connection
│   │   │   └── logging.py            # Structured logging
│   │   ├── 📂 models/                 # SQLAlchemy ORM models
│   │   │   ├── fishing_hub.py         # Port/harbor model
│   │   │   ├── pfz_zones.py           # PFZ zone model with PostGIS geometry
│   │   │   └── observation.py         # Ocean observation model
│   │   ├── 📂 services/              # Business logic
│   │   │   ├── orchestrator.py        # 🧠 Main pipeline coordinator
│   │   │   ├── scientific_engine.py   # 🔬 ORCA physics engine
│   │   │   ├── groq_service.py        # LLM integration (Groq API)
│   │   │   └── data_fetcher.py        # Live data from APIs
│   │   └── main.py                    # FastAPI application entry point
│   ├── 📂 alembic/                    # Database migrations
│   └── requirements.txt               # Python dependencies
│
├── 📂 frontend/                       # Next.js 14 Frontend
│   ├── 📂 app/                        # Next.js App Router
│   │   ├── layout.tsx                 # Root layout with providers
│   │   ├── page.tsx                   # Main application page
│   │   └── globals.css                # Global styles
│   ├── 📂 components/
│   │   ├── 📂 map/
│   │   │   └── MainMap.tsx            # 🗺️ MapLibre map with all layers
│   │   ├── 📂 copilot/
│   │   │   └── AICopilot.tsx          # 🤖 Chat interface
│   │   ├── 📂 panels/
│   │   │   ├── InfoPanel.tsx          # Side panel with port/zone details
│   │   │   └── FishingHubSelector.tsx # Port selection dropdown
│   │   ├── 📂 controls/
│   │   │   ├── LayerControl.tsx       # Toggle ocean data layers
│   │   │   └── StatusBar.tsx          # Connection status indicator
│   │   └── 📂 providers/
│   │       └── QueryProvider.tsx      # TanStack Query provider
│   ├── 📂 lib/
│   │   ├── store.ts                   # Zustand global state
│   │   └── api-client.ts             # Backend API client
│   └── package.json
│
├── 📂 docs/                           # Documentation
├── 📂 scripts/                        # Setup & deployment scripts
├── 📂 monitoring/                     # Prometheus + Grafana configs
├── docker-compose.yml                 # Full stack containerization
├── .env.example                       # Environment template
└── ORCA_Scientific_Ocean_Fishing_Reasoning_Rulebook.pdf
```

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ & **npm**
- **Python** 3.12+
- **PostgreSQL** 15+ with PostGIS (optional — system works without it)

### 1. Clone & Install

```bash
git clone https://github.com/kanglesoham11-code/sih_2026.git
cd sih_2026
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Create `.env` in the root directory:
```env
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5433/orca
ENVIRONMENT=development
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. Run

```bash
# Terminal 1 — Backend
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2 — Frontend
cd frontend
npm run dev
```

Open **http://localhost:3000** in your browser.

---

## 🔬 Scientific Engine

The scientific engine (`backend/app/services/scientific_engine.py`) implements all formulas from the **ORCA Scientific Ocean Fishing Reasoning Rulebook**:

| Module | Rulebook Section | Formula |
|--------|-----------------|---------|
| `SSTGradientEngine` | §2-3 | `\|∇SST\| = √((∂SST/∂x)² + (∂SST/∂y)²)` |
| `ChlorophyllEngine` | §4-5 | `log₁₀(CHL + ε)` normalization + gradient |
| `OceanCurrentEngine` | §7-11 | Vorticity `ζ = ∂v/∂x − ∂u/∂y`, Okubo-Weiss `W = Sn² + Ss² − ζ²` |
| `UpwellingEngine` | §12 | Ekman transport `M = τ / (ρ_w · f)`, multi-indicator detection |
| `FishingSuitabilityModel` | §16-17 | Weighted score with safety override |
| `PFZCalculator` | §24 | Full pipeline: SST + CHL + fronts + safety → ranked zones |
| `IndiaEEZBoundary` | — | Ray-casting point-in-polygon for EEZ enforcement |

### Anti-Hallucination Rule
The LLM (Groq) is **strictly prohibited** from generating coordinates, readings, or scientific values. It only **explains** the deterministic results from the scientific engine in simple language.

---

## 📡 API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/chat` | POST | AI copilot — accepts message + location, returns response + map actions |
| `/api/v1/observations` | GET | Current ocean observations (SST, CHL, waves, wind) |
| `/api/v1/pfz-zones` | GET | Predicted fishing zones with scores |
| `/api/v1/fishing-hubs` | GET | List of fishing ports/harbors |
| `/api/v1/warnings` | GET | Active weather/safety warnings |
| `/health` | GET | Service health check |

### Chat API Example

```json
// POST /api/v1/chat
{
  "message": "Where should I fish today?",
  "location": [72.8333, 18.9067]
}

// Response
{
  "response": "Head 12km southwest of Sassoon Dock...",
  "map_actions": [
    { "type": "fly_to", "longitude": 72.83, "latitude": 18.9 },
    { "type": "route_to_pfz", "start": [72.83, 18.9], "end": [72.71, 18.85] },
    { "type": "show_pfz_zones", "zones": [...] },
    { "type": "highlight_pfz", "pfz_id": "pfz-offshore-west" }
  ]
}
```

---

## 🇮🇳 Indian EEZ Boundary Enforcement

All Potential Fishing Zones are **strictly constrained** within India's international maritime boundaries using a ray-casting point-in-polygon algorithm.

The boundary polygon matches the **actual border line visible on OpenStreetMap nautical charts**, covering:

- **West Coast (Arabian Sea)**: Gujarat → Maharashtra → Goa → Karnataka → Kerala → Kanyakumari
- **East Coast (Bay of Bengal)**: Kanyakumari → Tamil Nadu → Andhra Pradesh → Odisha → West Bengal

```python
# Every candidate zone is checked:
if not IndiaEEZBoundary.is_within_indian_eez(zone_lon, zone_lat):
    continue  # Zone rejected — outside Indian waters
```

---

## 🖥️ Ocean Data Layers

| Layer | Data Source | Visualization |
|-------|-----------|---------------|
| 🌡️ Sea Surface Temperature (SST) | Open-Meteo Marine | Scattered dots (blue → yellow → red) |
| 🌿 Chlorophyll-a | Copernicus/MOSDAC | Scattered dots (dark → green → red) |
| 🧂 Salinity | INCOIS | Scattered dots (light cyan → dark teal) |
| 🌊 Wave Height | Open-Meteo Marine | Scattered dots (light → indigo → dark) |
| 💨 Wind Speed | Open-Meteo Weather | Scattered dots (light → purple → dark) |
| 🎯 PFZ Zones | Scientific Engine | Animated polygon boundaries |
| 🛣️ Route | Route Engine | Dashed red line (sea-only path) |

All layers use **land masking** — data points only render over water (transparent on land).

---

## 👥 Team

Built for **Smart India Hackathon (SIH) 2026** 🇮🇳

---

<p align="center">
  <b>ORCA — Because every fisherman deserves the power of satellite intelligence.</b>
</p>
