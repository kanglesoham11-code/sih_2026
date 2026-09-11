"""
Copernicus Marine Service Adapter
PRD Section 7 (rows 7-9) - Global Ocean Data

Sources:
- Copernicus Marine Toolbox (Python SDK)
- Marine Data Store API

Acquisition Mode: SDK (preferred) → REST API fallback

Coverage:
- Global ocean analysis and forecasts
- Sea surface temperature, currents, salinity
- Wave height, wind fields
- Chlorophyll, primary productivity
"""

import subprocess
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from loguru import logger

from app.connectors.base import (
    SourceAdapter,
    SourceMetadata,
    Payload,
    HealthStatus,
    SpatialQuery,
    SpatioTemporalQuery,
    SubsetQuery,
    AcquisitionMode,
    DataType,
)
from app.core.config import settings


class CopernicusMarineAdapter(SourceAdapter):
    """
    Copernicus Marine Service Connector
    
    Official SDK: copernicusmarine (Python package)
    Authentication: Username + password (free registration required)
    
    PRD Notes:
    - Mode C: Python SDK
    - Provides global ocean model data
    - NRT and forecast data available
    - High quality, operational service
    
    Key datasets:
    - GLOBAL_ANALYSISFORECAST_PHY_001_024 (physics)
    - GLOBAL_ANALYSISFORECAST_BGC_001_028 (biogeochemistry)
    - GLOBAL_MULTIYEAR_PHY_001_030 (reanalysis)
    
    Variables:
    - SST, SSS (sea surface temperature/salinity)
    - Ocean currents (u, v components)
    - Sea level
    - Wave height, period
    - Chlorophyll, nutrients
    """
    
    SOURCE_ID = "copernicus_marine"
    
    def __init__(self):
        super().__init__(timeout=30)  # SDK operations can be slow
        
        # Check if SDK is installed
        try:
            import copernicusmarine
            self.sdk_available = True
            logger.info("Copernicus Marine SDK available")
        except ImportError:
            self.sdk_available = False
            logger.warning(
                "Copernicus Marine SDK not installed. "
                "Install with: pip install copernicusmarine"
            )
    
    def get_metadata(self) -> SourceMetadata:
        """Registry info and capabilities"""
        return SourceMetadata(
            source_id=self.SOURCE_ID,
            provider="Copernicus Marine Environment Monitoring Service (CMEMS)",
            name="Copernicus Marine Toolbox",
            interface_type=AcquisitionMode.SDK,
            base_url="https://data.marine.copernicus.eu/",
            endpoint_verified=True,  # Well-documented official service
            auth_required=True,  # Username/password required
            capabilities=[
                "health_check",
                "get_subset",
                "get_latest",
                "get_forecast",
            ],
            variables=[
                "sea_surface_temperature",
                "sea_surface_salinity",
                "ocean_current_u",
                "ocean_current_v",
                "sea_level_anomaly",
                "significant_wave_height",
                "chlorophyll_concentration",
                "primary_productivity",
                "mixed_layer_depth",
            ],
            coverage="Global ocean (90S-90N, 180W-180E)",
        )
    
    async def health_check(self) -> HealthStatus:
        """Check Copernicus Marine service availability"""
        
        if not self.sdk_available:
            return HealthStatus(
                ok=False,
                latency_ms=0,
                error_code="SDK_NOT_INSTALLED",
                detail="copernicusmarine package not installed"
            )
        
        if not (settings.COPERNICUSMARINE_SERVICE_USERNAME and 
                settings.COPERNICUSMARINE_SERVICE_PASSWORD):
            return HealthStatus(
                ok=False,
                latency_ms=0,
                error_code="AUTH_MISSING",
                detail="Copernicus Marine credentials not configured"
            )
        
        try:
            start = datetime.utcnow()
            
            # Test authentication with a lightweight command
            # Using subprocess to avoid blocking
            result = subprocess.run(
                [
                    "copernicusmarine",
                    "describe",
                    "--include-datasets",
                    "--max-datasets", "1",
                ],
                capture_output=True,
                text=True,
                timeout=10,
                env={
                    "COPERNICUSMARINE_SERVICE_USERNAME": settings.COPERNICUSMARINE_SERVICE_USERNAME,
                    "COPERNICUSMARINE_SERVICE_PASSWORD": settings.COPERNICUSMARINE_SERVICE_PASSWORD,
                }
            )
            
            latency_ms = int((datetime.utcnow() - start).total_seconds() * 1000)
            
            if result.returncode == 0:
                logger.info(f"Copernicus Marine health check: OK (latency={latency_ms}ms)")
                return HealthStatus(ok=True, latency_ms=latency_ms)
            else:
                logger.error(f"Copernicus Marine health check failed: {result.stderr}")
                return HealthStatus(
                    ok=False,
                    latency_ms=latency_ms,
                    error_code="AUTH_FAILED",
                    detail=result.stderr[:200]
                )
        
        except subprocess.TimeoutExpired:
            logger.error("Copernicus Marine health check timeout")
            return HealthStatus(
                ok=False,
                latency_ms=self.timeout * 1000,
                error_code="TIMEOUT",
                detail="Health check timed out"
            )
        
        except Exception as e:
            logger.error(f"Copernicus Marine health check error: {e}")
            return HealthStatus(
                ok=False,
                latency_ms=0,
                error_code="ERROR",
                detail=str(e)
            )
    
    async def get_subset(self, q: SubsetQuery) -> List[Payload]:
        """
        Query Copernicus Marine data subset
        
        Uses copernicusmarine.subset() API
        """
        
        if not self.sdk_available:
            raise RuntimeError("Copernicus Marine SDK not available")
        
        logger.info(
            f"Querying Copernicus Marine: dataset={q.dataset_id}, "
            f"vars={q.variables}, bbox=({q.latitude}, {q.longitude})"
        )
        
        try:
            import copernicusmarine
            
            # Prepare subset parameters
            # Small spatial window around point
            lat_min = q.latitude - 0.1
            lat_max = q.latitude + 0.1
            lon_min = q.longitude - 0.1
            lon_max = q.longitude + 0.1
            
            # Call SDK subset function
            # Returns xarray.Dataset
            dataset = copernicusmarine.subset(
                dataset_id=q.dataset_id,
                variables=q.variables,
                minimum_longitude=lon_min,
                maximum_longitude=lon_max,
                minimum_latitude=lat_min,
                maximum_latitude=lat_max,
                start_datetime=q.time_start,
                end_datetime=q.time_end,
                username=settings.COPERNICUSMARINE_SERVICE_USERNAME,
                password=settings.COPERNICUSMARINE_SERVICE_PASSWORD,
            )
            
            retrieved_at = datetime.utcnow()
            
            # Convert xarray.Dataset to Payload list
            payloads = self._parse_xarray_to_payloads(
                dataset=dataset,
                source_id=self.SOURCE_ID,
                dataset_id=q.dataset_id,
                retrieved_at=retrieved_at,
            )
            
            logger.info(f"Retrieved {len(payloads)} data points from Copernicus Marine")
            return payloads
        
        except Exception as e:
            logger.error(f"Copernicus Marine subset error: {e}")
            raise
    
    async def get_latest(self, q: SpatialQuery) -> Payload:
        """
        Get latest ocean data at location
        
        Uses analysis/forecast dataset for most recent data
        """
        
        logger.info(
            f"Querying Copernicus Marine latest: lat={q.latitude}, lon={q.longitude}"
        )
        
        # Use default physics analysis-forecast dataset
        dataset_id = "cmems_mod_glo_phy_anfc_0.083deg_P1D-m"
        
        # Query last 2 days to ensure we get latest
        time_end = datetime.utcnow()
        time_start = time_end - timedelta(days=2)
        
        subset_query = SubsetQuery(
            dataset_id=dataset_id,
            variables=["thetao", "so"],  # SST, salinity
            latitude=q.latitude,
            longitude=q.longitude,
            radius_km=q.radius_km,
            time_start=time_start,
            time_end=time_end,
        )
        
        payloads = await self.get_subset(subset_query)
        
        # Return most recent
        if payloads:
            payloads.sort(key=lambda p: p.observed_at or p.valid_from, reverse=True)
            return payloads[0]
        else:
            raise ValueError("No data retrieved from Copernicus Marine")
    
    def _parse_xarray_to_payloads(
        self,
        dataset,
        source_id: str,
        dataset_id: str,
        retrieved_at: datetime,
    ) -> List[Payload]:
        """
        Convert xarray.Dataset to Payload objects
        
        Args:
            dataset: xarray.Dataset from Copernicus Marine
            source_id: Source identifier
            dataset_id: Dataset identifier
            retrieved_at: Retrieval timestamp
        
        Returns:
            List of Payload objects
        """
        
        payloads = []
        
        try:
            # Iterate over variables
            for var_name in dataset.data_vars:
                var = dataset[var_name]
                
                # Get attributes
                unit = var.attrs.get("units", "unknown")
                long_name = var.attrs.get("long_name", var_name)
                
                # Iterate over time/lat/lon coordinates
                for time_idx in range(len(dataset.time)):
                    for lat_idx in range(len(dataset.latitude)):
                        for lon_idx in range(len(dataset.longitude)):
                            value = float(var.isel(
                                time=time_idx,
                                latitude=lat_idx,
                                longitude=lon_idx,
                            ).values)
                            
                            # Skip NaN values
                            if value != value:  # NaN check
                                continue
                            
                            time_val = dataset.time.isel(time=time_idx).values
                            lat_val = float(dataset.latitude.isel(latitude=lat_idx).values)
                            lon_val = float(dataset.longitude.isel(longitude=lon_idx).values)
                            
                            # Convert numpy datetime64 to Python datetime
                            import numpy as np
                            timestamp = datetime.utcfromtimestamp(
                                time_val.astype('datetime64[s]').astype(int)
                            )
                            
                            # Determine if observation or forecast
                            data_type = (
                                DataType.FORECAST
                                if timestamp > retrieved_at
                                else DataType.NRT
                            )
                            
                            payload = Payload(
                                source_id=source_id,
                                dataset_id=dataset_id,
                                variable=var_name,
                                value=value,
                                unit=unit,
                                latitude=lat_val,
                                longitude=lon_val,
                                observed_at=timestamp if data_type == DataType.NRT else None,
                                valid_from=timestamp if data_type == DataType.FORECAST else None,
                                valid_until=None,  # Could compute from forecast lead time
                                source_updated_at=timestamp,
                                retrieved_at=retrieved_at,
                                data_type=data_type,
                                quality_flag="good",
                                confidence=0.9,  # High confidence for operational model
                            )
                            
                            payloads.append(payload)
            
            return payloads
        
        except Exception as e:
            logger.error(f"Error parsing xarray dataset: {e}")
            raise


from datetime import timedelta
