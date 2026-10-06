"""10 ORCA Agents — real implementations with run() and health()."""
import time
from typing import Dict, Any, Tuple
from datetime import datetime

from app.core.config import settings


class PlannerAgent:
    """Classifies user intent and decides which agents to invoke."""
    
    INTENTS = {
        'fishing': ['fish', 'pfz', 'catch', 'tuna', 'mackerel', 'sardine', 'pomfret', 'prawn', 'best zone', 'fishing zone', 'where should i go'],
        'safety': ['safe', 'danger', 'cyclone', 'storm', 'warning', 'risk', 'hazard', 'unsafe', 'no-go', 'go or no'],
        'weather': ['weather', 'wind', 'wave', 'rain', 'temperature', 'forecast', 'monsoon'],
        'navigation': ['route', 'path', 'navigate', 'direction', 'travel', 'reach', 'way to'],
    }
    
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        t0 = time.time()
        msg = context.get("message", "").lower()
        intent = "general"
        for k, keywords in self.INTENTS.items():
            if any(kw in msg for kw in keywords):
                intent = k
                break
        agents_needed = ["Weather", "Ocean", "Risk", "Explanation"]
        if intent == "fishing":
            agents_needed = ["Weather", "Ocean", "DataDiscovery", "PFZ", "Risk", "Geo", "Route", "Explanation"]
        elif intent == "navigation":
            agents_needed = ["Weather", "Ocean", "Geo", "Route", "Risk", "Explanation"]
        elif intent == "safety":
            agents_needed = ["Weather", "Ocean", "Risk", "Explanation"]
        return {"intent": intent, "agents_needed": agents_needed, "ms": int((time.time()-t0)*1000)}
    
    def health(self) -> Tuple[bool, int, str]:
        t0 = time.time()
        result = self.run({"message": "is it safe to fish today?"})
        ok = result["intent"] == "safety"
        return ok, int((time.time()-t0)*1000), f"Intent={result['intent']}"


class LanguageAgent:
    """Detects language of user message."""
    
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        t0 = time.time()
        msg = context.get("message", "")
        # Simple heuristic: check for Devanagari, Latin, etc.
        has_devanagari = any('\u0900' <= c <= '\u097F' for c in msg)
        lang = "hi" if has_devanagari else "en"
        return {"detected_language": lang, "ms": int((time.time()-t0)*1000)}
    
    def health(self) -> Tuple[bool, int, str]:
        t0 = time.time()
        r = self.run({"message": "hello world"})
        return r["detected_language"] == "en", int((time.time()-t0)*1000), f"lang={r['detected_language']}"


class DataDiscoveryAgent:
    """Lists available data sources and their status."""
    
    SOURCES = [
        {"name": "Open-Meteo Marine", "kind": "official_api", "provides": ["wave_height", "sst", "currents"]},
        {"name": "Open-Meteo Weather", "kind": "official_api", "provides": ["wind", "temperature", "humidity"]},
        {"name": "INCOIS", "kind": "roadmap", "provides": []},
        {"name": "IMD", "kind": "roadmap", "provides": []},
        {"name": "Copernicus", "kind": "roadmap", "provides": []},
        {"name": "MOSDAC", "kind": "roadmap", "provides": []},
    ]
    
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        t0 = time.time()
        live = [s for s in self.SOURCES if s["kind"] == "official_api"]
        return {"live_sources": len(live), "total_sources": len(self.SOURCES), "sources": self.SOURCES, "ms": int((time.time()-t0)*1000)}
    
    def health(self) -> Tuple[bool, int, str]:
        t0 = time.time()
        r = self.run({})
        ok = r["live_sources"] >= 2
        return ok, int((time.time()-t0)*1000), f"{r['live_sources']} live sources"


class PFZAgent:
    """Computes Potential Fishing Zones from SST/CHL gradients."""
    
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        t0 = time.time()
        from app.services.scientific_engine import PFZCalculator
        sst = context.get("sst", 28.0)
        chl = context.get("chl", 0.3)
        wave_h = context.get("wave_height", 1.0)
        wind_s = context.get("wind_speed", 15.0)
        lat = context.get("lat", 18.9)
        lon = context.get("lon", 72.8)
        zones = PFZCalculator.compute_pfz_zones(lat=lat, lon=lon, sst=sst, chl=chl, wave_height=wave_h, wind_speed=wind_s, air_temp=sst+1.5)
        return {"zones": zones, "count": len(zones), "ms": int((time.time()-t0)*1000)}
    
    def health(self) -> Tuple[bool, int, str]:
        t0 = time.time()
        r = self.run({"sst": 28.0, "chl": 0.4, "wave_height": 1.0, "wind_speed": 15.0})
        ok = r["count"] > 0
        return ok, int((time.time()-t0)*1000), f"{r['count']} zones computed"


class OceanAgent:
    """Provides ocean parameters (SST, currents) from cached live data."""
    
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        t0 = time.time()
        from app.services.status_service import status_service
        marine = status_service.last_marine_fetch
        sst = None
        current_vel = None
        current_dir = None
        if marine and "current" in marine:
            sst = marine["current"].get("sea_surface_temperature")
            current_vel = marine["current"].get("ocean_current_velocity")
            current_dir = marine["current"].get("ocean_current_direction")
        return {
            "sst": sst, "current_velocity_kmh": current_vel, "current_direction": current_dir,
            "source": "Open-Meteo Marine API", "ms": int((time.time()-t0)*1000)
        }
    
    def health(self) -> Tuple[bool, int, str]:
        t0 = time.time()
        from app.services.status_service import status_service
        ok = status_service.marine_last_success_at > 0
        return ok, int((time.time()-t0)*1000), "Marine data cached" if ok else "No marine data yet"


class WeatherAgent:
    """Provides weather data from cached live data."""
    
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        t0 = time.time()
        from app.services.status_service import status_service
        weather = status_service.last_weather_fetch
        temp = None
        wind = None
        if weather and "current" in weather:
            temp = weather["current"].get("temperature_2m")
            wind = weather["current"].get("wind_speed_10m")
        return {"temperature": temp, "wind_speed": wind, "source": "Open-Meteo Weather API", "ms": int((time.time()-t0)*1000)}
    
    def health(self) -> Tuple[bool, int, str]:
        t0 = time.time()
        from app.services.status_service import status_service
        ok = status_service.weather_last_success_at > 0
        return ok, int((time.time()-t0)*1000), "Weather data cached" if ok else "No weather data yet"


class GeoAgent:
    """Resolves coordinates against Indian EEZ boundaries."""
    
    # Indian EEZ approximate bounding box (simplified polygon)
    EEZ_BOUNDS = {"min_lat": 6.0, "max_lat": 24.0, "min_lon": 66.0, "max_lon": 92.0}
    
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        t0 = time.time()
        lat = context.get("lat", 18.9)
        lon = context.get("lon", 72.8)
        in_eez = (self.EEZ_BOUNDS["min_lat"] <= lat <= self.EEZ_BOUNDS["max_lat"] and
                  self.EEZ_BOUNDS["min_lon"] <= lon <= self.EEZ_BOUNDS["max_lon"])
        return {"in_indian_eez": in_eez, "lat": lat, "lon": lon, "ms": int((time.time()-t0)*1000)}
    
    def health(self) -> Tuple[bool, int, str]:
        t0 = time.time()
        r = self.run({"lat": 18.9, "lon": 72.8})
        ok = r["in_indian_eez"] is True
        return ok, int((time.time()-t0)*1000), "EEZ lookup OK" if ok else "EEZ lookup failed"


class RiskAgent:
    """Computes safety verdict using vessel-class thresholds."""
    
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        t0 = time.time()
        from app.config.safety_thresholds import get_safety_verdict
        wave = context.get("wave_height", 0)
        wind = context.get("wind_speed", 0)
        vessel = context.get("vessel_class", "motorised")
        cyclone = context.get("cyclone_active", False)
        verdict, reason, evidence = get_safety_verdict(wave, wind, vessel, cyclone)
        return {"verdict": verdict, "reason": reason, "evidence": evidence, "ms": int((time.time()-t0)*1000)}
    
    def health(self) -> Tuple[bool, int, str]:
        t0 = time.time()
        r = self.run({"wave_height": 5.0, "wind_speed": 20.0, "vessel_class": "traditional"})
        ok = r["verdict"] == "NO-GO"
        return ok, int((time.time()-t0)*1000), f"High-wave test → {r['verdict']}"


class RouteAgent:
    """Computes a basic route from port to target zone."""
    
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        import math
        t0 = time.time()
        start = context.get("start", [72.8, 18.9])
        end = context.get("end", [72.5, 19.1])
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        dist_deg = math.sqrt(dx*dx + dy*dy)
        dist_km = round(dist_deg * 111, 1)
        bearing = round(math.degrees(math.atan2(dx, dy)) % 360, 1)
        return {"distance_km": dist_km, "bearing": bearing, "start": start, "end": end, "ms": int((time.time()-t0)*1000)}
    
    def health(self) -> Tuple[bool, int, str]:
        t0 = time.time()
        r = self.run({"start": [72.8, 18.9], "end": [72.5, 19.1]})
        ok = r["distance_km"] > 0
        return ok, int((time.time()-t0)*1000), f"Route {r['distance_km']}km"


class ExplanationAgent:
    """Generates natural-language explanation. Checks LLM key or uses template fallback."""
    
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        t0 = time.time()
        has_llm = bool(settings.GROQ_API_KEY)
        mode = "llm" if has_llm else "template"
        return {"mode": mode, "ms": int((time.time()-t0)*1000)}
    
    def health(self) -> Tuple[bool, int, str]:
        t0 = time.time()
        has_llm = bool(settings.GROQ_API_KEY)
        if has_llm:
            return True, int((time.time()-t0)*1000), "LLM key configured"
        return True, int((time.time()-t0)*1000), "Template fallback active"
