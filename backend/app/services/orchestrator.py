"""
Agent Orchestrator
PRD Section 13 - Multi-Agent System Orchestration
Computes PFZ zones from LIVE Open-Meteo data when database is unavailable.
"""

import asyncio
import math
import uuid
from typing import Dict, Any, List
from loguru import logger
from datetime import datetime

from app.live_api import _fetch_open_meteo_marine, _fetch_open_meteo_weather


class RiskSafetyEngine:
    """Deterministic Safety Scoring Engine (PRD Section 12)"""
    
    @staticmethod
    def calculate_risk(wave_height: float, wind_speed: float) -> str:
        if wave_height > 4.0 or wind_speed > 60:
            return "CRITICAL_RISK - DO NOT SAIL"
        if wave_height > 2.5 or wind_speed > 40:
            return "HIGH_RISK - CAUTION ADVISED"
        return "SAFE_FOR_SAILING"


def _compute_pfz_from_live_data(
    lat: float, lon: float,
    sst: float, wave_h: float, wind_s: float, temp: float
) -> List[Dict[str, Any]]:
    """
    Compute Potential Fishing Zones using the Scientific Rulebook (PDF Section 24).
    Pipeline: SST + CHL → gradients → fronts → suitability → safety filter → zones.
    
    Uses the deterministic scientific engine — no LLM involvement.
    """
    from app.services.scientific_engine import PFZCalculator
    
    # Estimate chlorophyll from SST/wave proxy (in production, use Copernicus BGC data)
    # Coastal upwelling zones have higher chlorophyll when SST is lower and waves mix nutrients
    chl_estimate = max(0.1, 0.3 + (28 - sst) * 0.15 + min(wave_h, 2.0) * 0.1)
    
    zones = PFZCalculator.compute_pfz_zones(
        lat=lat,
        lon=lon,
        sst=sst,
        chl=chl_estimate,
        wave_height=wave_h,
        wind_speed=wind_s,
        air_temp=temp,
    )
    
    return zones

def _detect_intent(message: str) -> str:
    """Simple keyword-based intent detection."""
    msg = message.lower()
    fishing_kw = ['fish', 'pfz', 'catch', 'fishing', 'tuna', 'mackerel', 'sardine', 'pomfret', 'prawn', 'best zone', 'fishing zone', 'where should i go']
    safety_kw = ['safe', 'danger', 'cyclone', 'storm', 'warning', 'risk', 'hazard', 'launch', 'rocket', 'unsafe']
    weather_kw = ['weather', 'wind', 'wave', 'rain', 'temperature', 'forecast', 'monsoon', 'climate']
    route_kw = ['route', 'path', 'navigate', 'direction', 'travel', 'reach', 'way to', 'how to get']
    
    if any(k in msg for k in fishing_kw):
        return 'fishing'
    if any(k in msg for k in route_kw):
        return 'navigation'
    if any(k in msg for k in safety_kw):
        return 'safety'
    if any(k in msg for k in weather_kw):
        return 'weather'
    return 'general'


async def orchestrate_chat(message: str, location: List[float] = None) -> Dict[str, Any]:
    """
    Coordinates the agent pipeline using LIVE data:
    1. Fetch live ocean + weather from Open-Meteo
    2. Compute PFZ zones from SST/wave/wind physics
    3. Calculate risk assessment
    4. Generate map_actions for frontend
    """
    logger.info(f"Orchestrating chat for: {message}")
    intent = _detect_intent(message)
    logger.info(f"Detected intent: {intent}")
    
    pfz_data = []
    weather_ctx = ""
    risk_status = "UNKNOWN"
    map_actions = []
    
    wave_h = 0
    wind_s = 0
    sst = 27
    temp = 28
    
    # 1. Try database first, fall back to live computation (2s timeout)
    db_success = False
    try:
        from app.core.database import AsyncSessionLocal
        from sqlalchemy import select, text
        from app.models.pfz_zones import PFZZone
        
        async def _try_db():
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(PFZZone).limit(5))
                zones = result.scalars().all()
                for z in zones:
                    pfz_data.append({
                        "sector": z.sector,
                        "confidence": z.attributes.get("confidence_score") if z.attributes else None,
                        "valid_until": z.valid_until.isoformat() if z.valid_until else "unknown"
                    })
                return True
        
        db_success = await asyncio.wait_for(_try_db(), timeout=2.0)
    except Exception as e:
        logger.warning(f"Database unavailable (fast fallback): {e}")
    
    # 2. ALWAYS fetch live weather & ocean data
    if location and len(location) == 2:
        lon, lat = location
        try:
            marine, weather = await asyncio.gather(
                _fetch_open_meteo_marine(lat, lon),
                _fetch_open_meteo_weather(lat, lon),
            )
            
            wave_h = marine.get("current", {}).get("wave_height", 0) if marine else 0
            wind_s = weather.get("current", {}).get("wind_speed_10m", 0) if weather else 0
            temp = weather.get("current", {}).get("temperature_2m", 28) if weather else 28
            
            # Estimate SST from air temp (ocean is typically 1-2°C cooler near coast)
            sst = round(temp - 1.5, 1) if temp > 20 else 26.0
            
            risk_status = RiskSafetyEngine.calculate_risk(wave_h, wind_s)
            
            weather_ctx = (
                f"Live Location Data ({lat:.2f}N, {lon:.2f}E):\n"
                f"- Sea Surface Temperature: {sst}°C\n"
                f"- Wave Height: {wave_h}m\n"
                f"- Wind Speed: {wind_s}km/h\n"
                f"- Air Temp: {temp}°C\n"
                f"- Safety Risk Status: {risk_status}\n"
            )
        except Exception as e:
            logger.error(f"Live data fetch failed: {e}")
    
    # 3. Compute PFZ zones from live data ONLY for fishing/navigation intents
    live_zones = []
    if location and len(location) == 2 and intent in ('fishing', 'navigation'):
        lon, lat = location
        live_zones = _compute_pfz_from_live_data(lat, lon, sst, wave_h, wind_s, temp)
        
        if not db_success:
            pfz_data = [
                {"sector": z["name"], "confidence": z["score"], "valid_until": "live"}
                for z in live_zones
            ]
    
    # 4. Format context for LLM
    pfz_ctx = "Predicted PFZ Zones (from live ocean data):\n" + "\n".join(
        [f"- {z['sector']} (Productivity Score: {z['confidence']}, Valid: {z['valid_until']})" for z in pfz_data]
    )
    
    system_context = (
        "You are ORCA, an AI marine intelligence assistant. You have access to REAL-TIME ocean and weather data.\n"
        f"The user's question intent is: {intent}.\n"
        "The PFZ zones below were computed from live SST, wave height, and wind data using Copernicus-style physics.\n"
        "Do NOT invent data. Use ONLY the provided context.\n"
        "Give the user a SIMPLE, clear conclusion. Do NOT dump raw numbers or technical readings.\n"
        "Good answer: 'Go here, this is the best fishing area.' Bad answer: 'SST is 27.5°C, Chlorophyll is 0.42 mg/m³'\n"
        "The user only wants to know: Where to go? Is it safe? Which option is better?\n"
        "If the intent is 'safety' or 'weather', focus on weather conditions and safety, not fishing.\n"
        "If the intent is 'general', answer the question using available weather/ocean data as context.\n"
        "Always mention the safety status prominently.\n\n"
        f"--- LIVE CONTEXT ---\n"
        f"{weather_ctx}\n\n"
        f"{pfz_ctx}\n"
        f"--- END CONTEXT ---\n\n"
        "If Safety Risk is HIGH or CRITICAL, WARN the user not to sail."
    )
    
    # 5. Generate map_actions only for fishing/navigation intents
    if location and len(location) == 2 and live_zones and intent in ('fishing', 'navigation'):
        lon, lat = location
        best_zone = live_zones[0]  # Highest scoring zone
        
        map_actions.append({
            "type": "fly_to",
            "longitude": lon,
            "latitude": lat,
            "zoom": 10,
            "pitch": 50,
            "bearing": -30,
        })
        map_actions.append({
            "type": "route_to_pfz",
            "start": [lon, lat],
            "end": [best_zone["lon"], best_zone["lat"]],
        })
        map_actions.append({
            "type": "highlight_pfz",
            "pfz_id": best_zone["id"],
            "pfz_name": best_zone["name"],
            "pfz_score": best_zone["score"],
        })
        # Send ALL zones so frontend can display them
        map_actions.append({
            "type": "show_pfz_zones",
            "zones": live_zones,
        })
    
    # Also try DB map actions if DB is available
    if db_success and location and len(location) == 2:
        try:
            lon, lat = location
            async with AsyncSessionLocal() as db:
                result = await db.execute(text("""
                    SELECT id, ST_X(ST_Centroid(geom)) as pfz_lon, ST_Y(ST_Centroid(geom)) as pfz_lat
                    FROM pfz_zones
                    ORDER BY ST_Distance(geom::geography, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography)
                    LIMIT 1
                """), {"lat": lat, "lon": lon})
                row = result.fetchone()
                if row:
                    map_actions.append({
                        "type": "highlight_pfz",
                        "pfz_id": str(row[0])
                    })
        except Exception:
            pass

    return {
        "system_context": system_context,
        "risk_status": risk_status,
        "pfz_count": len(pfz_data),
        "map_actions": map_actions,
        "live_zones": live_zones,
        "intent": intent,
    }
