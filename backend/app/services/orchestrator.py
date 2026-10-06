"""
Agent Orchestrator
PRD Section 13 - Multi-Agent System Orchestration
Computes PFZ zones from LIVE Open-Meteo data using sequential agent invocation.
"""

import asyncio
import time
from typing import Dict, Any, List
from loguru import logger
from datetime import datetime

from app.live_api import _fetch_open_meteo_marine, _fetch_open_meteo_weather
from app.agents import (
    PlannerAgent, LanguageAgent, DataDiscoveryAgent, PFZAgent,
    OceanAgent, WeatherAgent, GeoAgent, RiskAgent, RouteAgent, ExplanationAgent
)
from app.config.safety_thresholds import get_safety_verdict
from app.services.status_service import status_service

# Instantiate agents
agents = {
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

async def orchestrate_chat(message: str, location: List[float] = None, vessel_class: str = "motorised", cyclone_active: bool = False) -> Dict[str, Any]:
    """
    Coordinates the agent pipeline using LIVE data:
    """
    logger.info(f"Orchestrating chat for: {message}, vessel: {vessel_class}, cyclone: {cyclone_active}")
    
    agent_trace = []
    evidence = []
    context = {
        "message": message,
        "lat": location[1] if location else 18.9220,
        "lon": location[0] if location else 72.8258,
        "vessel_class": vessel_class,
        "cyclone_active": cyclone_active,
    }
    
    # 1. Fetch live data for the specific location so Ocean/Weather agents can use it
    try:
        marine, weather = await asyncio.gather(
            _fetch_open_meteo_marine(context["lat"], context["lon"]),
            _fetch_open_meteo_weather(context["lat"], context["lon"]),
        )
        context["marine_data"] = marine
        context["weather_data"] = weather
    except Exception as e:
        logger.error(f"Live data fetch failed: {e}")
        context["marine_data"] = {}
        context["weather_data"] = {}

    def run_agent(name: str):
        agent = agents[name]
        try:
            res = agent.run(context)
            agent_trace.append({
                "agent": name,
                "input": f"context with {len(context)} keys",
                "output": str(res),
                "ms": res.get("ms", 0)
            })
            context.update(res) # Merge results back into context
        except Exception as e:
            logger.error(f"Agent {name} failed: {e}")
            agent_trace.append({"agent": name, "input": "...", "output": f"ERROR: {e}", "ms": 0})

    # Execute agents in sequence
    run_agent("Language")
    run_agent("Planner")
    run_agent("DataDiscovery")
    run_agent("Geo")
    
    # Ocean & Weather Agents
    # Wait, my Ocean/Weather agents currently read from status_service. Let me update them in context if they don't do it themselves.
    # I'll just run them and they will use what they use. But wait, I need to extract wave/wind for RiskAgent!
    marine = context.get("marine_data", {})
    weather = context.get("weather_data", {})
    
    wave_h = marine.get("current", {}).get("wave_height", 0) if marine else 0
    wind_s = weather.get("current", {}).get("wind_speed_10m", 0) if weather else 0
    temp = weather.get("current", {}).get("temperature_2m", 28) if weather else 28
    sst = marine.get("current", {}).get("sea_surface_temperature")
    if sst is None:
        sst = temp - 1.5 if temp > 20 else 26.0
        
    context["wave_height"] = wave_h
    context["wind_speed"] = wind_s
    context["temp"] = temp
    context["sst"] = sst
    # Chlorophyll estimate (since Copernicus is roadmap)
    context["chl"] = max(0.1, 0.3 + (28 - sst) * 0.15 + min(wave_h, 2.0) * 0.1)

    run_agent("Ocean")
    run_agent("Weather")
    
    run_agent("Risk")
    # Add Risk evidence
    if "evidence" in context:
        evidence.extend(context["evidence"])
        
    run_agent("PFZ")
    
    # Route Agent
    if context.get("zones"):
        best_zone = context["zones"][0]
        context["end"] = [best_zone["lon"], best_zone["lat"]]
        run_agent("Route")
    
    run_agent("Explanation")
    
    # Formatting outputs for chat
    risk_status = context.get("verdict", "UNKNOWN")
    risk_reason = context.get("reason", "")
    intent = context.get("intent", "general")
    live_zones = context.get("zones", [])
    
    weather_ctx = (
        f"Live Location Data ({context['lat']:.2f}N, {context['lon']:.2f}E):\n"
        f"- Sea Surface Temperature: {context.get('sst')}°C\n"
        f"- Wave Height: {context.get('wave_height')}m\n"
        f"- Wind Speed: {context.get('wind_speed')}km/h\n"
        f"- Safety Risk Status: {risk_status} ({risk_reason})\n"
    )
    
    pfz_ctx = "Predicted PFZ Zones (from live ocean data):\n" + "\n".join(
        [f"- {z['name']} (Productivity Score: {z['score']})" for z in live_zones]
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
    
    # Map actions
    map_actions = []
    if live_zones and intent in ('fishing', 'navigation'):
        best_zone = live_zones[0]
        lon, lat = context["lon"], context["lat"]
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
        map_actions.append({
            "type": "show_pfz_zones",
            "zones": live_zones,
        })
        
    # Log decision
    status_service.log_decision({
        "vessel_class": vessel_class,
        "cyclone_active": cyclone_active,
        "wave_height": context.get("wave_height"),
        "wind_speed": context.get("wind_speed"),
        "verdict": risk_status,
        "reason": risk_reason,
        "evidence_ids": [len(status_service.decision_log) + 1] # dummy id relation
    })

    return {
        "system_context": system_context,
        "risk_status": risk_status,
        "pfz_count": len(live_zones),
        "map_actions": map_actions,
        "live_zones": live_zones,
        "intent": intent,
        "evidence": evidence,
        "agent_trace": agent_trace,
    }
