import asyncio
import time
from typing import Dict, Any, List
from datetime import datetime
from loguru import logger
import httpx

from app.core.config import settings

# Agents
from app.agents.planner import PlannerAgent
from app.agents.language import LanguageAgent
from app.agents.data_discovery import DataDiscoveryAgent
from app.agents.pfz_agent import PfzAgentAgent
from app.agents.ocean import OceanAgent
from app.agents.weather import WeatherAgent
from app.agents.geo import GeoAgent
from app.agents.risk import RiskAgent
from app.agents.route import RouteAgent
from app.agents.explanation import ExplanationAgent

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
            "PFZ": PfzAgentAgent(),
            "Ocean": OceanAgent(),
            "Weather": WeatherAgent(),
            "Geo": GeoAgent(),
            "Risk": RiskAgent(),
            "Route": RouteAgent(),
            "Explanation": ExplanationAgent(),
        }
        
    async def fetch_marine(self):
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get("https://marine-api.open-meteo.com/v1/marine?latitude=15&longitude=73&current=wave_height")
                if resp.status_code == 200:
                    self.last_marine_fetch = resp.json()
                    self.marine_last_success_at = time.time()
        except Exception as e:
            logger.warning(f"Marine fetch failed: {e}")

    async def fetch_weather(self):
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get("https://api.open-meteo.com/v1/forecast?latitude=15&longitude=73&current=temperature_2m")
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
                    # Override real latency if the self-check was instantaneous
                    real_latency = int((time.time() - start_t) * 1000)
                    if latency < real_latency:
                        latency = real_latency
                    
                    self.agents_state[name] = {
                        "name": name,
                        "status": "online" if ok else "offline",
                        "last_run_at": datetime.utcnow().isoformat() + "Z",
                        "latency_ms": latency if latency > 0 else 5,
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
            "note": "Live wave data"
        })
        
        weather_age = int(now - self.weather_last_success_at) if self.weather_last_success_at else -1
        sources.append({
            "name": "Open-Meteo Weather",
            "kind": "official_api",
            "status": "live" if weather_age >= 0 and weather_age < 120 else ("cached" if self.weather_last_success_at else "down"),
            "last_success_at": datetime.utcfromtimestamp(self.weather_last_success_at).isoformat() + "Z" if self.weather_last_success_at else None,
            "age_seconds": weather_age if weather_age >= 0 else None,
            "refresh_interval_s": 60,
            "note": "Live weather data"
        })
        
        # Roadmap sources
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
            # Fallback before first loop completes
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
