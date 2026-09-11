"""
API Response Schemas
PRD Section 20.1 - API Endpoints
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Overall system status")
    timestamp: datetime = Field(..., description="Check timestamp")
    sources: Dict[str, Any] = Field(..., description="Individual source health")


class DataPointResponse(BaseModel):
    """Single data point response"""
    source_id: str
    dataset_id: Optional[str] = None
    variable: str
    value: float
    unit: str
    latitude: float
    longitude: float
    observed_at: Optional[datetime] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    source_updated_at: Optional[datetime] = None
    retrieved_at: datetime
    data_type: str
    quality_flag: Optional[str] = "good"
    confidence: Optional[float] = None
    provenance_url: Optional[str] = None


class DataSubsetResponse(BaseModel):
    """Dataset subset response"""
    query: Dict[str, Any] = Field(..., description="Original query parameters")
    count: int = Field(..., description="Number of data points returned")
    data: List[DataPointResponse] = Field(..., description="Data points")
    retrieved_at: datetime = Field(..., description="Query execution timestamp")
    freshness: Optional[str] = Field(None, description="Data freshness classification")


class ChatResponse(BaseModel):
    """Agent chat response"""
    message: str = Field(..., description="Agent response message")
    session_id: str = Field(..., description="Session ID")
    mode: str = Field(..., description="Query mode used")
    data_retrieved: Optional[bool] = Field(False, description="Whether live data was fetched")
    sources_used: Optional[List[str]] = Field(default_factory=list, description="Data sources consulted")
    recommendations: Optional[List[str]] = Field(None, description="Action recommendations")


class PFZZoneResponse(BaseModel):
    """Potential Fishing Zone response"""
    zone_id: str
    forecast_date: datetime
    latitude: float
    longitude: float
    suitability_score: float = Field(..., ge=0, le=1)
    species: Optional[List[str]] = None
    environmental_factors: Dict[str, float]
    confidence: float = Field(..., ge=0, le=1)


class PFZForecastResponse(BaseModel):
    """PFZ forecast response"""
    query: Dict[str, Any]
    forecast_date: datetime
    zones: List[PFZZoneResponse]
    metadata: Dict[str, Any]


class WarningResponse(BaseModel):
    """Warning or advisory response"""
    warning_id: str
    source_id: str
    warning_type: str
    severity: str
    title: str
    description: str
    issued_at: datetime
    valid_until: Optional[datetime] = None
    affected_region: Optional[str] = None
    geometry: Optional[Dict[str, Any]] = None


class WarningListResponse(BaseModel):
    """List of warnings"""
    query: Dict[str, Any]
    count: int
    warnings: List[WarningResponse]
    retrieved_at: datetime


class RouteSegment(BaseModel):
    """Single route segment"""
    segment_index: int
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float
    distance_km: float
    estimated_duration_hours: float
    weather_conditions: Optional[Dict[str, Any]] = None
    risk_level: Optional[str] = None


class RouteOptimizationResponse(BaseModel):
    """Route optimization response"""
    route_id: str
    segments: List[RouteSegment]
    total_distance_km: float
    estimated_duration_hours: float
    fuel_estimate: Optional[float] = None
    safety_score: float = Field(..., ge=0, le=1)
    warnings: Optional[List[str]] = None
    alternate_routes: Optional[List[Dict[str, Any]]] = None


class FreshnessReportResponse(BaseModel):
    """Data freshness report"""
    report_timestamp: datetime
    sources: Dict[str, Dict[str, Any]]


class ErrorResponse(BaseModel):
    """Error response"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
