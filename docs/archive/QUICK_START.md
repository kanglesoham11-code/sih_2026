# 🌊 ORCA Quick Start Guide

## One-Command Start

**Double-click:** `START_ORCA.bat`

This will automatically:
1. ✅ Check Docker is running
2. ✅ Start PostgreSQL, Redis, MinIO
3. ✅ Install dependencies if needed
4. ✅ Start backend server (port 8000)
5. ✅ Start frontend server (port 3000)

## Access the Platform

After ~30 seconds:

- **Frontend Dashboard:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## What You'll See

### 🗺️ Interactive Map Dashboard
- **Large map view** (90% of screen) centered on Indian Ocean
- **AI Copilot** on the right side for natural language queries
- **Layer controls** on the left to toggle data layers
- **Search bar** at the top to find locations
- **Status bar** at the bottom showing connection status

### 🤖 AI Features
- Ask questions in natural language
- Get fishing zone recommendations
- Query weather conditions
- Request safety warnings
- Navigate with voice commands

### 📊 Data Layers
- **Fishing Zones:** Potential Fishing Zones (PFZ)
- **Ocean Parameters:** SST, Chlorophyll, Currents, Salinity
- **Weather:** Wind, Waves, Precipitation
- **Hazards:** Cyclone tracks, Active warnings
- **Geography:** EEZ boundaries, Ports, Bathymetry
- **Ecology:** Coral reefs, Protected areas

## Demo Mode

If backend is not connected, the platform runs in **Demo Mode**:
- Shows sample data and UI
- AI responses explain what real system would do
- All UI components fully functional
- Clear yellow banner indicating demo state

## Testing the System

### Test 1: Search Location
1. Click search bar (top left)
2. Type "Mumbai" or "Chennai"
3. Click result to fly to location

### Test 2: Toggle Layers
1. Click "Layers" button (left side)
2. Expand "Fishing Zones"
3. Toggle PFZ layer on/off

### Test 3: Ask AI Copilot
1. Click AI icon (right side) if closed
2. Type: "Show me fishing zones near my location"
3. Get intelligent response

### Test 4: Select Location
1. Click anywhere on map
2. Info panel appears with ocean data
3. View temperature, chlorophyll, weather

### Test 5: Time Control
1. Click date control (bottom right)
2. Change date to see forecasts
3. Navigate through time

## Troubleshooting

### Port Already in Use
```bash
# Stop running servers
netstat -ano | findstr :3000
netstat -ano | findstr :8000
taskkill /PID <process_id> /F
```

### Docker Not Running
1. Start Docker Desktop
2. Wait for Docker to fully start
3. Run `START_ORCA.bat` again

### Frontend Won't Start
```bash
cd frontend
rmdir /s /q node_modules
rmdir /s /q .next
npm install
npm run dev
```

### Backend Won't Start
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Dependencies Missing
```bash
# Frontend
cd frontend
npm install

# Backend
cd backend
pip install -r requirements.txt
```

## Manual Start (Alternative)

### Terminal 1 - Docker
```bash
docker-compose up -d
```

### Terminal 2 - Backend
```bash
cd backend
venv\Scripts\activate.bat
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 3 - Frontend
```bash
cd frontend
npm install
npm run dev
```

## Features Overview

### 🎯 Core Capabilities
- ✅ Real-time marine data visualization
- ✅ AI-powered natural language interface
- ✅ Multi-source data integration
- ✅ PFZ forecast display
- ✅ Cyclone tracking
- ✅ Weather overlays
- ✅ Location-based recommendations
- ✅ Time-series data navigation
- ✅ Mobile-responsive design

### 🔌 Data Sources (when connected)
- INCOIS ERDDAP (Ocean observations)
- IMD Weather (Meteorological data)
- Copernicus Marine (Global ocean data)
- MOSDAC (Satellite imagery)

### 🛡️ Safety Features
- Active warning display
- Cyclone tracking
- High seas alerts
- Freshness indicators
- Data provenance

## Getting Live Link (ngrok)

```bash
# Install ngrok
choco install ngrok

# Expose frontend
ngrok http 3000
```

Copy the generated URL to access from anywhere!

## Next Steps

1. ✅ Start the system: `START_ORCA.bat`
2. ✅ Open http://localhost:3000
3. ✅ Explore the interface
4. ✅ Test AI queries
5. ✅ Review API docs at http://localhost:8000/docs
6. ✅ Check data freshness indicators
7. ✅ Toggle different layer categories
8. ✅ Select locations for detailed info

## Support

- 📖 Full docs: `docs/` directory
- 🔧 Troubleshooting: `TROUBLESHOOTING.md`
- 🏗️ Architecture: `docs/architecture.md`
- 📡 API Reference: `docs/API.md`

---

**Ready to explore marine intelligence! 🌊🐟🚢**
