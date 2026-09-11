"""
India Meteorological Department (IMD) Weather Adapter
PRD Section 7 (rows 5-6) - Weather Intelligence Data

Sources:
- IMD Public API (if available) - Row 5
- IMD Open Data Portal - Row 6

Acquisition Mode: REST API (preferred) → Web Fallback
"""

import httpx
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from loguru import logger

from app.connectors.base import (
    SourceAdapter,
    SourceMetadata,
    Payload,
    HealthStatus,
    SpatialQuery,
    SpatioTemporalQuery,
    AcquisitionMode,
    DataType,
)
from app.core.config import settings


class IMDWeatherAdapter(SourceAdapter):
    """
    IMD Weather Data Connector
    
    PRD Notes:
    - Official API: https://api.imd.gov.in/ (endpoint verification needed)
    - Open Data Portal: https://mausam.imd.gov.in/
    - Authentication: Verify if API key required
    - Coverage: India and Indian Ocean region
    
    Data types:
    - Current weather observations
    - Marine weather forecasts
    - Cyclone warnings and tracks
    - Wave height, wind speed, precipitation
    """
    
    SOURCE_ID = "imd_weather"
    BASE_URL = settings.IMD_API_BASE
    
    def __init__(self):
        super().__init__(timeout=10)
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            headers=self._get_headers(),
        )
    
    def _get_headers(self) -> Dict[str, str]:
        """Build request headers with optional API key"""
        headers = {
            "User-Agent": "ORCA/1.0",
            "Accept": "application/json",
        }
        
        if settings.IMD_API_KEY:
            headers["Authorization"] = f"Bearer {settings.IMD_API_KEY}"
        elif settings.IMD_USERNAME and settings.IMD_PASSWORD:
            # Basic auth if needed
            import base64
            credentials = f"{settings.IMD_USERNAME}:{settings.IMD_PASSWORD}"
            encoded = base64.b64encode(credentials.encode()).decode()
            headers["Authorization"] = f"Basic {encoded}"
        
        return headers
    
    def get_metadata(self) -> SourceMetadata:
        """Registry info and capabilities"""
        return SourceMetadata(
            source_id=self.SOURCE_ID,
            provider="India Meteorological Department",
            name="IMD Weather API",
            interface_type=AcquisitionMode.REST_API,
            base_url=self.BASE_URL,
            endpoint_verified=False,  # PRD Section 4.3 - needs verification
            auth_required=bool(settings.IMD_API_KEY or settings.IMD_USERNAME),
            capabilities=[
                "health_check",
                "get_latest",
                "get_forecast",
                "get_warnings",
            ],
            variables=[
                "air_temperature",
                "sea_surface_temperature",
                "wind_speed",
                "wind_direction",
                "wave_height",
                "precipitation",
                "pressure",
                "humidity",
                "visibility",
            ],
            coverage="India and Indian Ocean",
        )
    
    async def health_check(self) -> HealthStatus:
        """Check IMD API availability"""
        try:
            start = datetime.utcnow()
            
            # Try a lightweight endpoint (adjust based on actual API)
            # This is a placeholder - actual endpoint needs verification
            response = await self.client.get(f"{self.BASE_URL}status")
            
            latency_ms = int((datetime.utcnow() - start).total_seconds() * 1000)
            
            if response.status_code == 200:
                logger.info(f"IMD Weather health check: OK (latency={latency_ms}ms)")
                return HealthStatus(ok=True, latency_ms=latency_ms)
            
            elif response.status_code == 401:
                logger.error("IMD API authentication failed")
                return HealthStatus(
                    ok=False,
                    latency_ms=latency_ms,
                    error_code="AUTH_FAILED",
                    detail="Invalid credentials"
                )
            
            else:
                logger.warning(f"IMD API returned status {response.status_code}")
                return HealthStatus(
                    ok=False,
                    latency_ms=latency_ms,
                    error_code="PROVIDER_DOWN",
                    detail=f"HTTP {response.status_code}"
                )
        
        except httpx.TimeoutException:
            logger.error("IMD API health check timeout")
            return HealthStatus(
                ok=False,
                latency_ms=self.timeout * 1000,
                error_code="TIMEOUT",
                detail="Health check timed out"
            )
        
        except Exception as e:
            logger.error(f"IMD API health check failed: {e}")
            return HealthStatus(
                ok=False,
                latency_ms=0,
                error_code="PROVIDER_DOWN",
                detail=str(e)
            )
    
    async def get_latest(self, q: SpatialQuery) -> Payload:
        """
        Get latest weather observation
        
        PRD Section 7 - Current weather data
        """
        
        logger.info(
            f"Querying IMD weather: lat={q.latitude}, lon={q.longitude}"
        )
        
        try:
            # Placeholder endpoint - needs verification
            # Actual IMD API structure needs to be discovered
            endpoint = f"{self.BASE_URL}weather/current"
            
            params = {
                "lat": q.latitude,
                "lon": q.longitude,
                "radius": q.radius_km,
            }
            
            response = await self.client.get(endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            retrieved_at = datetime.utcnow()
            
            # Parse response (structure TBD based on actual API)
            # This is a placeholder normalization
            return Payload(
                source_id=self.SOURCE_ID,
                dataset_id="imd_current_weather",
                variable="air_temperature",
                value=data.get("temperature", 0.0),
                unit="celsius",
                latitude=q.latitude,
                longitude=q.longitude,
                observed_at=datetime.fromisoformat(data["timestamp"])
                if "timestamp" in data
                else None,
                valid_from=None,
                valid_until=None,
                source_updated_at=datetime.fromisoformat(data["updated_at"])
                if "updated_at" in data
                else None,
                retrieved_at=retrieved_at,
                data_type=DataType.OBSERVATION,
                quality_flag=data.get("quality", "good"),
            )
        
        except httpx.HTTPStatusError as e:
            logger.error(f"IMD API HTTP error: {e}")
            raise
        
        except Exception as e:
            logger.error(f"IMD get_latest error: {e}")
            raise
    
    async def get_forecast(self, q: SpatioTemporalQuery) -> List[Payload]:
        """
        Get weather forecast
        
        PRD Section 7 - Marine weather forecasts
        """
        
        logger.info(
            f"Querying IMD forecast: lat={q.latitude}, lon={q.longitude}, "
            f"time_range={q.time_start} to {q.time_end}"
        )
        
        try:
            # Placeholder endpoint
            endpoint = f"{self.BASE_URL}forecast/marine"
            
            params = {
                "lat": q.latitude,
                "lon": q.longitude,
                "start": q.time_start.isoformat(),
                "end": q.time_end.isoformat(),
            }
            
            response = await self.client.get(endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            retrieved_at = datetime.utcnow()
            
            # Parse forecast data (structure TBD)
            payloads = []
            
            for forecast in data.get("forecasts", []):
                payloads.append(
                    Payload(
                        source_id=self.SOURCE_ID,
                        dataset_id="imd_marine_forecast",
                        variable=forecast.get("variable", "wind_speed"),
                        value=forecast.get("value", 0.0),
                        unit=forecast.get("unit", "m/s"),
                        latitude=q.latitude,
                        longitude=q.longitude,
                        observed_at=None,
                        valid_from=datetime.fromisoformat(forecast["valid_from"])
                        if "valid_from" in forecast
                        else None,
                        valid_until=datetime.fromisoformat(forecast["valid_until"])
                        if "valid_until" in forecast
                        else None,
                        source_updated_at=datetime.fromisoformat(data["updated_at"])
                        if "updated_at" in data
                        else None,
                        retrieved_at=retrieved_at,
                        data_type=DataType.FORECAST,
                        confidence=forecast.get("confidence", 0.8),
                    )
                )
            
            return payloads
        
        except httpx.HTTPStatusError as e:
            logger.error(f"IMD API HTTP error: {e}")
            raise
        
        except Exception as e:
            logger.error(f"IMD get_forecast error: {e}")
            raise
    
    async def get_warnings(self, q: SpatialQuery) -> List[Dict[str, Any]]:
        """
        Get marine warnings and cyclone alerts
        
        PRD Section 7 - Cyclone warnings
        """
        
        logger.info(
            f"Querying IMD warnings: lat={q.latitude}, lon={q.longitude}"
        )
        
        try:
            # Placeholder endpoint
            endpoint = f"{self.BASE_URL}warnings/marine"
            
            params = {
                "lat": q.latitude,
                "lon": q.longitude,
                "radius": q.radius_km,
            }
            
            response = await self.client.get(endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse warnings (structure TBD)
            warnings = []
            
            for warning in data.get("warnings", []):
                warnings.append({
                    "source_id": self.SOURCE_ID,
                    "warning_type": warning.get("type", "marine_warning"),
                    "severity": warning.get("severity", "moderate"),
                    "title": warning.get("title", ""),
                    "description": warning.get("description", ""),
                    "issued_at": warning.get("issued_at"),
                    "valid_until": warning.get("valid_until"),
                    "affected_region": warning.get("region"),
                })
            
            return warnings
        
        except httpx.HTTPStatusError as e:
            logger.error(f"IMD API HTTP error: {e}")
            raise
        
        except Exception as e:
            logger.error(f"IMD get_warnings error: {e}")
            raise
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
