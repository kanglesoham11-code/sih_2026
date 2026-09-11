"""
API Request Schemas
PRD Section 20.1 - API Endpoints
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class SpatialQueryRequest(BaseModel):
    """Base spatial query parameters"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")
    radius_km: Optional[float] = Field(50.0, gt=0, le=500, description="Search radius in kilometers")


class TemporalQueryRequest(SpatialQueryRequest):
    """Spatio-temporal query parameters"""
    time_start: datetime = Field(..., description="Query start time (ISO 8601)")
    time_end: datetime = Field(..., description="Query end time (ISO 8601)")
    
    @field_validator("time_end")
    @classmethod
    def end_after_start(cls, v: datetime, info) -> datetime:
        """Validate time_end is after time_start"""
        if "time_start" in info.data and v <= info.data["time_start"]:
            raise ValueError("time_end must be after time_start")
        return v


class DataSubsetRequest(TemporalQueryRequest):
    """Dataset subset query"""
    source_id: str = Field(..., description="Source identifier (e.g., 'incois_erddap')")
    dataset_id: str = Field(..., description="Dataset identifier")
    variables: List[str] = Field(..., min_length=1, description="List of variables to retrieve")


class ChatRequest(BaseModel):
    """Agent chat request"""
    message: str = Field(..., min_length=1, description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    context: Optional[dict] = Field(default_factory=dict, description="Additional context")
    mode: Optional[str] = Field("standard", pattern="^(standard|live)$", description="Query mode")


class PFZQueryRequest(SpatialQueryRequest):
    """Potential Fishing Zone query"""
    forecast_days: Optional[int] = Field(7, ge=1, le=10, description="Forecast horizon in days")
    species: Optional[List[str]] = Field(None, description="Target fish species (optional)")


class RouteOptimizationRequest(BaseModel):
    """Route optimization request"""
    start_lat: float = Field(..., ge=-90, le=90)
    start_lon: float = Field(..., ge=-180, le=180)
    end_lat: float = Field(..., ge=-90, le=90)
    end_lon: float = Field(..., ge=-180, le=180)
    departure_time: datetime = Field(..., description="Departure time")
    vessel_type: Optional[str] = Field("fishing", description="Vessel type")
    optimize_for: Optional[str] = Field("safety", pattern="^(safety|fuel|time)$")
    avoid_zones: Optional[List[str]] = Field(None, description="Zone types to avoid")


class WarningQueryRequest(SpatialQueryRequest):
    """Warning and advisory query"""
    severity: Optional[List[str]] = Field(None, description="Filter by severity levels")
    warning_types: Optional[List[str]] = Field(None, description="Filter by warning types")
