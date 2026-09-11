"""
Ocean Intelligence Agent
PRD Section 13.6 - Ocean conditions analysis
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from loguru import logger

from app.agents.base import BaseAgent, AgentRole, AgentContext, AgentResponse
from app.connectors.base import SpatialQuery


class OceanIntelligenceAgent(BaseAgent):
    """
    Provides ocean condition analysis
    
    Analyzes:
    - Sea surface temperature (SST)
    - Sea surface salinity (SSS)
    - Ocean currents (speed and direction)
    - Wave height and period
    - Mixed layer depth
    - Chlorophyll concentration
    """
    
    def __init__(self, llm_client=None, gateway=None):
        super().__init__(AgentRole.OCEAN_INTELLIGENCE, llm_client)
        self.gateway = gateway
    
    async def process(self, context: AgentContext) -> AgentResponse:
        """Process ocean conditions query"""
        
        logger.info("Processing ocean intelligence query")
        
        # Extract location
        location = self._extract_location(context)
        
        if not location:
            return AgentResponse(
                agent_role=self.role,
                message="I need a location to provide ocean conditions. Please specify coordinates or a place name.",
                confidence=0.3,
            )
        
        # Check if live data is available
        if context.query_mode.value != "live" or not self.gateway:
            return await self._provide_general_ocean_info(context, location)
        
        # Gather live ocean data
        try:
            ocean_data = await self._gather_ocean_data(location)
            
            # Analyze conditions
            analysis = self._analyze_conditions(ocean_data)
            
            # Format response
            message = self._format_ocean_response(location, ocean_data, analysis)
            
            return AgentResponse(
                agent_role=self.role,
                message=message,
                data={
                    "location": location,
                    "ocean_data": ocean_data,
                    "analysis": analysis,
                },
                sources_used=["copernicus_marine", "incois_erddap"],
                confidence=0.9,
            )
        
        except Exception as e:
            logger.error(f"Error processing ocean query: {e}")
            return AgentResponse(
                agent_role=self.role,
                message=f"I encountered an issue retrieving ocean data: {str(e)}",
                confidence=0.0,
            )
    
    def _extract_location(self, context: AgentContext) -> Optional[Dict[str, float]]:
        """Extract location from context"""
        if context.location:
            return context.location
        if "location" in context.entities:
            return context.entities["location"]
        return None
    
    async def _gather_ocean_data(self, location: Dict[str, float]) -> Dict[str, Any]:
        """Gather ocean data from sources"""
        
        logger.info(f"Gathering ocean data at {location}")
        
        # TODO: Implement actual data gathering via gateway
        # query = SpatialQuery(
        #     latitude=location["latitude"],
        #     longitude=location["longitude"],
        #     radius_km=50,
        # )
        # 
        # sst = await self.gateway.get_latest("copernicus_marine", query)
        # currents = await self.gateway.get_latest("copernicus_marine", query)
        
        # Placeholder data
        ocean_data = {
            "sst": 28.3,
            "sst_unit": "celsius",
            "sss": 35.2,
            "sss_unit": "psu",
            "current_u": 0.15,  # m/s eastward
            "current_v": -0.22,  # m/s northward
            "current_speed": 0.27,
            "current_direction": 235,  # degrees
            "wave_height": 1.5,
            "wave_period": 8,
            "wave_direction": 270,
            "mixed_layer_depth": 45,
            "chlorophyll": 0.6,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        return ocean_data
    
    def _analyze_conditions(self, ocean_data: Dict[str, Any]) -> Dict[str, str]:
        """Analyze ocean conditions"""
        
        analysis = {}
        
        # SST analysis
        sst = ocean_data.get("sst", 0)
        if sst < 20:
            analysis["sst"] = "Cold water - limited biological activity"
        elif 20 <= sst < 25:
            analysis["sst"] = "Cool water - moderate productivity"
        elif 25 <= sst < 30:
            analysis["sst"] = "Warm water - high productivity, favorable for fishing"
        else:
            analysis["sst"] = "Very warm water - potential thermal stress"
        
        # Current analysis
        current_speed = ocean_data.get("current_speed", 0)
        if current_speed < 0.2:
            analysis["currents"] = "Weak currents - stable conditions"
        elif 0.2 <= current_speed < 0.5:
            analysis["currents"] = "Moderate currents - normal conditions"
        else:
            analysis["currents"] = "Strong currents - exercise caution"
        
        # Wave analysis
        wave_height = ocean_data.get("wave_height", 0)
        if wave_height < 1.5:
            analysis["waves"] = "Calm seas - safe for small vessels"
        elif 1.5 <= wave_height < 3.0:
            analysis["waves"] = "Moderate seas - suitable for most vessels"
        else:
            analysis["waves"] = "Rough seas - caution advised"
        
        # Chlorophyll analysis
        chl = ocean_data.get("chlorophyll", 0)
        if chl < 0.1:
            analysis["productivity"] = "Low productivity - oligotrophic waters"
        elif 0.1 <= chl < 1.0:
            analysis["productivity"] = "Moderate productivity - mesotrophic waters"
        else:
            analysis["productivity"] = "High productivity - eutrophic waters"
        
        return analysis
    
    def _format_ocean_response(
        self,
        location: Dict[str, float],
        ocean_data: Dict[str, Any],
        analysis: Dict[str, str],
    ) -> str:
        """Format natural language response"""
        
        lat = location["latitude"]
        lon = location["longitude"]
        
        message = f"**Ocean Conditions at ({lat:.2f}°, {lon:.2f}°)**\n\n"
        
        message += "**Physical Parameters:**\n"
        message += f"- Sea Surface Temperature: {ocean_data.get('sst', 'N/A')}°C\n"
        message += f"  ↳ {analysis.get('sst', '')}\n"
        message += f"- Sea Surface Salinity: {ocean_data.get('sss', 'N/A')} PSU\n"
        message += f"- Ocean Current: {ocean_data.get('current_speed', 'N/A')} m/s at {ocean_data.get('current_direction', 'N/A')}°\n"
        message += f"  ↳ {analysis.get('currents', '')}\n"
        message += f"- Wave Height: {ocean_data.get('wave_height', 'N/A')} m\n"
        message += f"- Wave Period: {ocean_data.get('wave_period', 'N/A')} seconds\n"
        message += f"  ↳ {analysis.get('waves', '')}\n\n"
        
        message += "**Biological Parameters:**\n"
        message += f"- Chlorophyll: {ocean_data.get('chlorophyll', 'N/A')} mg/m³\n"
        message += f"  ↳ {analysis.get('productivity', '')}\n"
        message += f"- Mixed Layer Depth: {ocean_data.get('mixed_layer_depth', 'N/A')} m\n\n"
        
        message += f"*Data retrieved at: {ocean_data.get('timestamp', 'Unknown')}*"
        
        return message
    
    async def _provide_general_ocean_info(
        self,
        context: AgentContext,
        location: Dict[str, float],
    ) -> AgentResponse:
        """Provide general ocean information"""
        
        message = f"Ocean conditions near ({location['latitude']:.2f}°, {location['longitude']:.2f}°):\n\n"
        message += "For live ocean data, enable LIVE mode. General information:\n\n"
        message += "**Typical conditions for this region:**\n"
        message += "- Average SST: 26-29°C (varies by season)\n"
        message += "- Typical current speeds: 0.1-0.5 m/s\n"
        message += "- Wave heights: 1-3 m (depending on monsoon)\n\n"
        message += "**Data sources available:**\n"
        message += "- Copernicus Marine: Global ocean analysis and forecasts\n"
        message += "- INCOIS ERDDAP: Indian Ocean satellite observations\n"
        message += "- IMD: Marine weather observations\n\n"
        message += "Enable LIVE mode for current, location-specific conditions."
        
        return AgentResponse(
            agent_role=self.role,
            message=message,
            confidence=0.5,
            requires_live_data=True,
        )
