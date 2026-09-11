"""
PFZ Intelligence Agent
PRD Section 13.5 - Potential Fishing Zone recommendations
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from loguru import logger

from app.agents.base import BaseAgent, AgentRole, AgentContext, AgentResponse
from app.connectors.base import SpatialQuery, SubsetQuery


class PFZIntelligenceAgent(BaseAgent):
    """
    Provides Potential Fishing Zone recommendations
    
    PRD Section 14 - PFZ Forecasting
    
    Analyzes:
    - Chlorophyll concentration (primary productivity)
    - Sea surface temperature (SST)
    - Ocean currents
    - Historical catch data
    - Bathymetry (depth zones)
    
    Outputs:
    - Suitability scores for fishing zones
    - Species-specific recommendations
    - Temporal forecasts (1-7 days)
    """
    
    # Optimal ranges for fishing (empirical values)
    OPTIMAL_SST_RANGE = (24, 30)  # Celsius
    OPTIMAL_CHLOROPHYLL_RANGE = (0.2, 2.0)  # mg/m³
    OPTIMAL_DEPTH_RANGE = (50, 200)  # meters
    
    def __init__(self, llm_client=None, gateway=None):
        super().__init__(AgentRole.PFZ_INTELLIGENCE, llm_client)
        self.gateway = gateway
    
    async def process(self, context: AgentContext) -> AgentResponse:
        """
        Process PFZ query
        
        Steps:
        1. Extract location and time range
        2. Gather environmental data (SST, chlorophyll, currents)
        3. Calculate suitability scores
        4. Generate recommendations
        """
        
        logger.info("Processing PFZ intelligence query")
        
        # Extract parameters
        location = self._extract_location(context)
        time_range = self._extract_time_range(context)
        species = context.entities.get("species", [])
        
        if not location:
            return AgentResponse(
                agent_role=self.role,
                message="I need a location to provide fishing zone recommendations. Please specify coordinates or a place name.",
                confidence=0.3,
            )
        
        # Check if live data is available
        if not context.query_mode.value == "live" or not self.gateway:
            return await self._provide_general_pfz_guidance(context, location, species)
        
        # Gather live environmental data
        try:
            env_data = await self._gather_environmental_data(location, time_range)
            
            # Calculate PFZ suitability
            suitability_score = self._calculate_suitability(env_data)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                location, env_data, suitability_score, species
            )
            
            # Format response
            message = self._format_pfz_response(
                location, env_data, suitability_score, recommendations
            )
            
            return AgentResponse(
                agent_role=self.role,
                message=message,
                data={
                    "location": location,
                    "suitability_score": suitability_score,
                    "environmental_data": env_data,
                    "recommendations": recommendations,
                },
                sources_used=[
                    "copernicus_marine",
                    "incois_erddap",
                    "imd_weather",
                ],
                confidence=0.85,
                recommendations=recommendations,
            )
        
        except Exception as e:
            logger.error(f"Error processing PFZ query: {e}")
            return AgentResponse(
                agent_role=self.role,
                message=f"I encountered an issue analyzing fishing zones: {str(e)}. Please try again.",
                confidence=0.0,
            )
    
    def _extract_location(self, context: AgentContext) -> Optional[Dict[str, float]]:
        """Extract location from context"""
        if context.location:
            return context.location
        
        if "location" in context.entities:
            return context.entities["location"]
        
        return None
    
    def _extract_time_range(self, context: AgentContext) -> Dict[str, datetime]:
        """Extract or default time range"""
        if context.time_range:
            return context.time_range
        
        # Default: next 24 hours
        now = datetime.utcnow()
        return {
            "start": now,
            "end": now + timedelta(days=1),
        }
    
    async def _gather_environmental_data(
        self,
        location: Dict[str, float],
        time_range: Dict[str, datetime],
    ) -> Dict[str, Any]:
        """
        Gather environmental data from sources
        """
        
        logger.info(f"Gathering environmental data for PFZ at {location}")
        
        # TODO: Implement actual data gathering via gateway
        # This is a placeholder structure
        
        query = SpatialQuery(
            latitude=location["latitude"],
            longitude=location["longitude"],
            radius_km=50,
        )
        
        # Gather data from multiple sources
        # sst_data = await self.gateway.get_latest("copernicus_marine", query)
        # chlorophyll_data = await self.gateway.get_latest("copernicus_marine", query)
        # current_data = await self.gateway.get_latest("copernicus_marine", query)
        
        # Placeholder data
        env_data = {
            "sst": 27.5,  # Celsius
            "sst_unit": "celsius",
            "chlorophyll": 0.8,  # mg/m³
            "chlorophyll_unit": "mg/m³",
            "current_speed": 0.3,  # m/s
            "current_direction": 180,  # degrees
            "depth": 120,  # meters
            "wave_height": 1.2,  # meters
            "wind_speed": 8,  # m/s
        }
        
        return env_data
    
    def _calculate_suitability(self, env_data: Dict[str, Any]) -> float:
        """
        Calculate fishing zone suitability score (0-1)
        
        PRD Section 14.2 - PFZ Algorithm
        
        Factors:
        - SST within optimal range
        - Chlorophyll concentration (primary productivity)
        - Suitable depth
        - Moderate currents
        - Safe weather conditions
        """
        
        scores = []
        
        # SST score
        sst = env_data.get("sst", 0)
        if self.OPTIMAL_SST_RANGE[0] <= sst <= self.OPTIMAL_SST_RANGE[1]:
            sst_score = 1.0
        elif sst < self.OPTIMAL_SST_RANGE[0] - 5 or sst > self.OPTIMAL_SST_RANGE[1] + 5:
            sst_score = 0.0
        else:
            # Linear decay outside optimal range
            distance = min(
                abs(sst - self.OPTIMAL_SST_RANGE[0]),
                abs(sst - self.OPTIMAL_SST_RANGE[1])
            )
            sst_score = max(0, 1 - (distance / 5))
        scores.append(("sst", sst_score, 0.3))
        
        # Chlorophyll score (indicator of productivity)
        chl = env_data.get("chlorophyll", 0)
        if self.OPTIMAL_CHLOROPHYLL_RANGE[0] <= chl <= self.OPTIMAL_CHLOROPHYLL_RANGE[1]:
            chl_score = 1.0
        elif chl < 0.1 or chl > 5.0:
            chl_score = 0.0
        else:
            chl_score = 0.5
        scores.append(("chlorophyll", chl_score, 0.4))
        
        # Depth score
        depth = env_data.get("depth", 0)
        if self.OPTIMAL_DEPTH_RANGE[0] <= depth <= self.OPTIMAL_DEPTH_RANGE[1]:
            depth_score = 1.0
        elif depth < 20 or depth > 500:
            depth_score = 0.0
        else:
            depth_score = 0.6
        scores.append(("depth", depth_score, 0.2))
        
        # Weather safety score
        wave_height = env_data.get("wave_height", 0)
        wind_speed = env_data.get("wind_speed", 0)
        
        if wave_height < 2 and wind_speed < 15:
            safety_score = 1.0
        elif wave_height > 4 or wind_speed > 25:
            safety_score = 0.0
        else:
            safety_score = 0.5
        scores.append(("safety", safety_score, 0.1))
        
        # Weighted average
        total_score = sum(score * weight for _, score, weight in scores)
        
        logger.info(f"Suitability calculated: {total_score:.2f}")
        return total_score
    
    def _generate_recommendations(
        self,
        location: Dict[str, float],
        env_data: Dict[str, Any],
        suitability_score: float,
        species: List[str],
    ) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # Overall suitability
        if suitability_score >= 0.7:
            recommendations.append("✅ Conditions are favorable for fishing")
        elif suitability_score >= 0.4:
            recommendations.append("⚠️ Conditions are moderate - fish with caution")
        else:
            recommendations.append("❌ Conditions are poor - not recommended for fishing")
        
        # SST-based recommendations
        sst = env_data.get("sst", 0)
        if sst < 24:
            recommendations.append("Water temperature is cooler than optimal - target deeper waters")
        elif sst > 30:
            recommendations.append("Water temperature is warmer - fish during early morning or evening")
        
        # Chlorophyll-based recommendations
        chl = env_data.get("chlorophyll", 0)
        if chl > 1.0:
            recommendations.append("High chlorophyll indicates good productivity - favorable for pelagic species")
        elif chl < 0.2:
            recommendations.append("Low chlorophyll - productivity may be limited")
        
        # Weather-based recommendations
        wave_height = env_data.get("wave_height", 0)
        if wave_height > 2.5:
            recommendations.append("⚠️ High waves - exercise caution, consider postponing")
        
        # Species-specific guidance
        if species:
            for sp in species:
                recommendations.append(f"For {sp}: Check local catch reports for recent activity")
        
        # Best time recommendation
        recommendations.append("🕐 Best fishing times: Early morning (5-8 AM) and evening (5-7 PM)")
        
        return recommendations
    
    def _format_pfz_response(
        self,
        location: Dict[str, float],
        env_data: Dict[str, Any],
        suitability_score: float,
        recommendations: List[str],
    ) -> str:
        """Format natural language response"""
        
        lat = location["latitude"]
        lon = location["longitude"]
        
        # Overall assessment
        if suitability_score >= 0.7:
            assessment = "excellent fishing conditions"
        elif suitability_score >= 0.4:
            assessment = "moderate fishing conditions"
        else:
            assessment = "poor fishing conditions"
        
        message = f"**Fishing Zone Analysis for ({lat:.2f}°, {lon:.2f}°)**\n\n"
        message += f"Overall Suitability: {suitability_score:.0%} - {assessment}\n\n"
        
        message += "**Environmental Conditions:**\n"
        message += f"- Sea Surface Temperature: {env_data.get('sst', 'N/A')}°C\n"
        message += f"- Chlorophyll: {env_data.get('chlorophyll', 'N/A')} mg/m³\n"
        message += f"- Current Speed: {env_data.get('current_speed', 'N/A')} m/s\n"
        message += f"- Wave Height: {env_data.get('wave_height', 'N/A')} m\n"
        message += f"- Wind Speed: {env_data.get('wind_speed', 'N/A')} m/s\n\n"
        
        message += "**Recommendations:**\n"
        for rec in recommendations:
            message += f"- {rec}\n"
        
        return message
    
    async def _provide_general_pfz_guidance(
        self,
        context: AgentContext,
        location: Dict[str, float],
        species: List[str],
    ) -> AgentResponse:
        """Provide general guidance without live data"""
        
        message = f"For fishing near ({location['latitude']:.2f}°, {location['longitude']:.2f}°), "
        message += "here are general recommendations:\n\n"
        message += "- Check INCOIS PFZ advisories published daily\n"
        message += "- Monitor IMD marine weather forecasts\n"
        message += "- Optimal SST for most species: 24-30°C\n"
        message += "- Look for areas with chlorophyll 0.2-2.0 mg/m³\n"
        message += "- Best fishing depths: 50-200 meters\n"
        message += "- Avoid fishing during high wave warnings\n\n"
        message += "For live, location-specific recommendations, please enable LIVE mode."
        
        return AgentResponse(
            agent_role=self.role,
            message=message,
            confidence=0.6,
            requires_live_data=True,
        )
