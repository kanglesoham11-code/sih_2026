import asyncio
import time
from typing import Dict, Any, List
from datetime import datetime
from loguru import logger
import httpx

from app.core.config import settings
from app.agents import (
    PlannerAgent, LanguageAgent, DataDiscoveryAgent, PFZAgent,
    OceanAgent, WeatherAgent, GeoAgent, RiskAgent, RouteAgent, ExplanationAgent,
)


class StatusService:
    def __init__(self):
        self.last_marine_fetch: Dict[str, Any] = {}
        self.last_weather_fetch: Dict[str, Any] = {}
        self.marine_last_success_at: float = 0
        self.weather_last_success_at: float = 0
        
        self.agents_state: Dict[str, Any] = {}
        self.agents = {
            "Planner": PlannerAgent(),
            "Language": LanguageAgent(),
            "DataDiscovery": DataDiscoveryAgent(),
            "PFZ": PFZAgent(),
            "Ocean": OceanAgent(),
            "Weather": WeatherAgent(),
            "Geo": GeoAgent(),
            "Risk": RiskAgent(),
            "Route": RouteAgent(),
            "Explanation": ExplanationAgent(),
        }
        
        # Decision audit log (in-memory)
        self.decision_log: List[Dict[str, Any]] = []
        
    def log_decision(self, decision: Dict[str, Any]):
        """Store a decision in the in-memory audit log."""
        decision["id"] = len(self.decision_log) + 1
        decision["timestamp"] = datetime.utcnow().isoformat() + "Z"
        self.decision_log.append(decision)
        # Keep last 100
        if len(self.decision_log) > 100:
            self.decision_log = self.decision_log[-100:]
        
    async def fetch_marine(self):
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    "https://marine-api.open-meteo.com/v1/marine",
                    params={
                        "latitude": 18.9, "longitude": 72.8,
                        "current": "wave_height,wave_direction,wave_period,swell_wave_height,ocean_current_velocity,ocean_current_direction,sea_surface_temperature",
                    }
                )
                if resp.status_code == 200:
                    self.last_marine_fetch = resp.json()
                    self.marine_last_success_at = time.time()
        except Exception as e:
            logger.warning(f"Marine fetch failed: {e}")

    async def fetch_weather(self):
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    "https://api.open-meteo.com/v1/forecast",
                    params={
                        "latitude": 18.9, "longitude": 72.8,
                        "current": "temperature_2m,wind_speed_10m,wind_direction_10m,relative_humidity_2m",
                    }
                )
                if resp.status_code == 200:
                    self.last_weather_fetch = resp.json()
                    self.weather_last_success_at = time.time()
        except Exception as e:
            logger.warning(f"Weather fetch failed: {e}")

    async def _data_loop(self):
        while True:
            await asyncio.gather(self.fetch_marine(), self.fetch_weather())
            await asyncio.sleep(60)
            
    async def _agent_loop(self):
        while True:
            for name, agent in self.agents.items():
                try:
                    start_t = time.time()
                    ok, latency, msg = agent.health()
                    real_latency = max(latency, int((time.time() - start_t) * 1000))
                    
                    self.agents_state[name] = {
                        "name": name,
                        "status": "online" if ok else "offline",
                        "last_run_at": datetime.utcnow().isoformat() + "Z",
                        "latency_ms": real_latency if real_latency > 0 else 1,
                        "check": msg
                    }
                except Exception as e:
                    self.agents_state[name] = {
                        "name": name,
                        "status": "offline",
                        "last_run_at": datetime.utcnow().isoformat() + "Z",
                        "latency_ms": 0,
                        "check": str(e)
                    }
            await asyncio.sleep(30)

    def start_loops(self):
        asyncio.create_task(self._data_loop())
        asyncio.create_task(self._agent_loop())

    def get_status(self) -> Dict[str, Any]:
        now = time.time()
        
        sources = []
        marine_age = int(now - self.marine_last_success_at) if self.marine_last_success_at else -1
        sources.append({
            "name": "Open-Meteo Marine",
            "kind": "official_api",
            "status": "live" if marine_age >= 0 and marine_age < 120 else ("cached" if self.marine_last_success_at else "down"),
            "last_success_at": datetime.utcfromtimestamp(self.marine_last_success_at).isoformat() + "Z" if self.marine_last_success_at else None,
            "age_seconds": marine_age if marine_age >= 0 else None,
            "refresh_interval_s": 60,
            "note": "Live SST, waves, currents"
        })
        
        weather_age = int(now - self.weather_last_success_at) if self.weather_last_success_at else -1
        sources.append({
            "name": "Open-Meteo Weather",
            "kind": "official_api",
            "status": "live" if weather_age >= 0 and weather_age < 120 else ("cached" if self.weather_last_success_at else "down"),
            "last_success_at": datetime.utcfromtimestamp(self.weather_last_success_at).isoformat() + "Z" if self.weather_last_success_at else None,
            "age_seconds": weather_age if weather_age >= 0 else None,
            "refresh_interval_s": 60,
            "note": "Live wind, temperature, humidity"
        })
        
        for roadmap_src in ["INCOIS", "IMD", "Copernicus", "MOSDAC", "BHASHINI"]:
            sources.append({
                "name": roadmap_src,
                "kind": "roadmap",
                "status": "planned",
                "last_success_at": None,
                "age_seconds": None,
                "refresh_interval_s": None,
                "note": "Adapter planned"
            })
            
        agents = list(self.agents_state.values())
        if not agents:
            agents = [{"name": n, "status": "offline", "last_run_at": None, "latency_ms": 0, "check": "Initializing"} for n in self.agents.keys()]
            
        agents_online = sum(1 for a in agents if a["status"] == "online")
        
        official_live = any(s["status"] == "live" for s in sources if s["kind"] == "official_api")
        
        if official_live and agents_online >= 8:
            system_status = "live"
        elif (official_live and agents_online > 0) or any(s["status"] == "cached" for s in sources if s["kind"] == "official_api"):
            system_status = "degraded"
        else:
            system_status = "offline"
            
        return {
            "system": system_status,
            "checked_at": datetime.utcnow().isoformat() + "Z",
            "data_sources": sources,
            "agents": agents,
            "agents_online": agents_online,
            "agents_total": len(self.agents)
        }

status_service = StatusService()
