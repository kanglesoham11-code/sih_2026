"""
Weather Intelligence Agent
PRD Section 13.7 - Marine weather analysis
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from loguru import logger

from app.agents.base import BaseAgent, AgentRole, AgentContext, AgentResponse
from app.connectors.base import SpatialQuery, SpatioTemporalQuery


class WeatherIntelligenceAgent(BaseAgent):
    """
    Provides marine weather analysis and forecasts
    
    Analyzes:
    - Wind speed and direction
    - Wave height, period, direction
    - Precipitation
    - Visibility
    - Air temperature
    - Atmospheric pressure
    - Cyclone warnings
    """
    
    # Safety thresholds
    SAFE_WIND_SPEED = 15  # m/s (knots * 0.514)
    SAFE_WAVE_HEIGHT = 3  # meters
    SAFE_VISIBILITY = 5  # km
    
    def __init__(self, llm_client=None, gateway=None):
        super().__init__(AgentRole.WEATHER_INTELLIGENCE, llm_client)
        self.gateway = gateway
    
    async def process(self, context: AgentContext) -> AgentResponse:
        """Process weather query"""
        
        logger.info("Processing weather intelligence query")
        
        # Extract parameters
        location = self._extract_location(context)
        forecast_requested = self._is_forecast_query(context)
        
        if not location:
            return AgentResponse(
                agent_role=self.role,
                message="I need a location to provide weather information. Please specify coordinates or a place name.",
                confidence=0.3,
            )
        
        # Check if live data is available
        if context.query_mode.value != "live" or not self.gateway:
            return await self._provide_general_weather_info(context, location)
        
        # Gather weather data
        try:
            if forecast_requested:
                weather_data = await self._get_forecast(location)
            else:
                weather_data = await self._get_current_weather(location)
            
            # Assess safety
            safety_assessment = self._assess_safety(weather_data)
            
            # Check for warnings
            warnings = await self._check_warnings(location)
            
            # Format response
            message = self._format_weather_response(
                location, weather_data, safety_assessment, warnings, forecast_requested
            )
            
            return AgentResponse(
                agent_role=self.role,
                message=message,
                data={
                    "location": location,
                    "weather": weather_data,
                    "safety": safety_assessment,
                    "warnings": warnings,
                },
                sources_used=["imd_weather", "copernicus_marine"],
                confidence=0.85,
            )
        
        except Exception as e:
            logger.error(f"Error processing weather query: {e}")
            return AgentResponse(
                agent_role=self.role,
                message=f"I encountered an issue retrieving weather data: {str(e)}",
                confidence=0.0,
            )
    
    def _extract_location(self, context: AgentContext) -> Optional[Dict[str, float]]:
        """Extract location from context"""
        if context.location:
            return context.location
        if "location" in context.entities:
            return context.entities["location"]
        return None
    
    def _is_forecast_query(self, context: AgentContext) -> bool:
        """Check if user wants forecast"""
        message = context.user_message.lower()
        forecast_keywords = ["forecast", "tomorrow", "will be", "going to", "future", "next"]
        return any(keyword in message for keyword in forecast_keywords)
    
    async def _get_current_weather(self, location: Dict[str, float]) -> Dict[str, Any]:
        """Get current weather conditions"""
        
        logger.info(f"Fetching current weather at {location}")
        
        # TODO: Implement via gateway
        # query = SpatialQuery(
        #     latitude=location["latitude"],
        #     longitude=location["longitude"],
        #     radius_km=50,
        # )
        # weather = await self.gateway.get_latest("imd_weather", query)
        
        # Placeholder data
        weather_data = {
            "type": "current",
            "wind_speed": 8.5,  # m/s
            "wind_direction": 180,  # degrees
            "wave_height": 1.8,  # meters
            "wave_period": 7,  # seconds
            "wave_direction": 200,  # degrees
            "air_temperature": 29,  # celsius
            "visibility": 10,  # km
            "pressure": 1012,  # hPa
            "humidity": 75,  # %
            "precipitation": 0,  # mm/hr
            "cloud_cover": 40,  # %
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        return weather_data
    
    async def _get_forecast(self, location: Dict[str, float]) -> Dict[str, Any]:
        """Get weather forecast"""
        
        logger.info(f"Fetching weather forecast at {location}")
        
        # TODO: Implement via gateway
        # Placeholder forecast for next 24 hours
        forecast_data = {
            "type": "forecast",
            "valid_from": datetime.utcnow().isoformat(),
            "valid_until": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
            "wind_speed": 10.2,
            "wind_direction": 195,
            "wave_height": 2.3,
            "wave_period": 8,
            "air_temperature": 28,
            "visibility": 8,
            "precipitation_probability": 20,  # %
            "conditions": "Partly cloudy",
        }
        
        return forecast_data
    
    def _assess_safety(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess marine safety based on weather"""
        
        wind_speed = weather_data.get("wind_speed", 0)
        wave_height = weather_data.get("wave_height", 0)
        visibility = weather_data.get("visibility", 10)
        
        # Safety flags
        safe_wind = wind_speed <= self.SAFE_WIND_SPEED
        safe_waves = wave_height <= self.SAFE_WAVE_HEIGHT
        safe_visibility = visibility >= self.SAFE_VISIBILITY
        
        # Overall safety
        if safe_wind and safe_waves and safe_visibility:
            overall = "SAFE"
            message = "Conditions are safe for marine activities"
        elif not safe_wind or not safe_waves:
            overall = "CAUTION"
            message = "Exercise caution - conditions are marginal"
        else:
            overall = "UNSAFE"
            message = "Conditions are unsafe - avoid marine activities"
        
        return {
            "overall": overall,
            "message": message,
            "safe_wind": safe_wind,
            "safe_waves": safe_waves,
            "safe_visibility": safe_visibility,
            "wind_status": self._wind_status(wind_speed),
            "wave_status": self._wave_status(wave_height),
        }
    
    def _wind_status(self, wind_speed: float) -> str:
        """Classify wind conditions"""
        if wind_speed < 5:
            return "Light winds"
        elif wind_speed < 10:
            return "Moderate winds"
        elif wind_speed < 15:
            return "Fresh winds"
        elif wind_speed < 20:
            return "Strong winds - caution"
        else:
            return "Very strong winds - unsafe"
    
    def _wave_status(self, wave_height: float) -> str:
        """Classify wave conditions"""
        if wave_height < 1:
            return "Calm seas"
        elif wave_height < 2:
            return "Slight seas"
        elif wave_height < 3:
            return "Moderate seas"
        elif wave_height < 4:
            return "Rough seas - caution"
        else:
            return "Very rough seas - unsafe"
    
    async def _check_warnings(self, location: Dict[str, float]) -> List[Dict[str, str]]:
        """Check for active weather warnings"""
        
        logger.info(f"Checking warnings at {location}")
        
        # TODO: Implement via gateway
        # query = SpatialQuery(
        #     latitude=location["latitude"],
        #     longitude=location["longitude"],
        #     radius_km=200,
        # )
        # warnings = await self.gateway.get_warnings("imd_weather", query)
        
        # Placeholder - no active warnings
        return []
    
    def _format_weather_response(
        self,
        location: Dict[str, float],
        weather_data: Dict[str, Any],
        safety: Dict[str, Any],
        warnings: List[Dict],
        is_forecast: bool,
    ) -> str:
        """Format natural language response"""
        
        lat = location["latitude"]
        lon = location["longitude"]
        
        time_label = "Forecast" if is_forecast else "Current Conditions"
        
        message = f"**Marine Weather - {time_label}**\n"
        message += f"**Location:** ({lat:.2f}°, {lon:.2f}°)\n\n"
        
        # Safety status
        safety_emoji = {
            "SAFE": "✅",
            "CAUTION": "⚠️",
            "UNSAFE": "❌",
        }
        emoji = safety_emoji.get(safety["overall"], "❓")
        message += f"**Safety Status:** {emoji} {safety['overall']}\n"
        message += f"*{safety['message']}*\n\n"
        
        # Weather details
        message += "**Weather Conditions:**\n"
        message += f"- Wind: {weather_data.get('wind_speed', 'N/A')} m/s from {weather_data.get('wind_direction', 'N/A')}°\n"
        message += f"  ↳ {safety.get('wind_status', '')}\n"
        message += f"- Waves: {weather_data.get('wave_height', 'N/A')} m, period {weather_data.get('wave_period', 'N/A')}s\n"
        message += f"  ↳ {safety.get('wave_status', '')}\n"
        message += f"- Air Temperature: {weather_data.get('air_temperature', 'N/A')}°C\n"
        message += f"- Visibility: {weather_data.get('visibility', 'N/A')} km\n"
        message += f"- Pressure: {weather_data.get('pressure', 'N/A')} hPa\n"
        message += f"- Humidity: {weather_data.get('humidity', 'N/A')}%\n"
        
        if is_forecast:
            message += f"- Precipitation Probability: {weather_data.get('precipitation_probability', 'N/A')}%\n"
            message += f"- Conditions: {weather_data.get('conditions', 'N/A')}\n"
        
        # Warnings
        if warnings:
            message += f"\n**⚠️ Active Warnings ({len(warnings)}):**\n"
            for warning in warnings:
                message += f"- {warning.get('title', 'Warning')}: {warning.get('severity', 'Unknown')}\n"
        
        # Timestamp
        timestamp = weather_data.get("timestamp") or weather_data.get("valid_from", "Unknown")
        message += f"\n*Data time: {timestamp}*"
        
        return message
    
    async def _provide_general_weather_info(
        self,
        context: AgentContext,
        location: Dict[str, float],
    ) -> AgentResponse:
        """Provide general weather information"""
        
        message = f"Weather information for ({location['latitude']:.2f}°, {location['longitude']:.2f}°):\n\n"
        message += "For live weather data, enable LIVE mode.\n\n"
        message += "**General marine weather guidance:**\n"
        message += "- Safe wind speeds: < 15 m/s (~30 knots)\n"
        message += "- Safe wave heights: < 3 meters\n"
        message += "- Minimum safe visibility: 5 km\n"
        message += "- Always check IMD marine warnings before departure\n"
        message += "- Avoid going out during monsoon season (June-September)\n"
        message += "- Best weather window: October-May\n\n"
        message += "Enable LIVE mode for current conditions and forecasts."
        
        return AgentResponse(
            agent_role=self.role,
            message=message,
            confidence=0.5,
            requires_live_data=True,
        )
