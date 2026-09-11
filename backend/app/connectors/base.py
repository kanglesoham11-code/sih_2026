"""
Base Source Adapter
PRD Section 3.1, 4.1
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class DataType(str, Enum):
    """Data type classification - PRD Section 31"""
    OBSERVATION = "observation"
    NRT = "nrt"
    FORECAST = "forecast"
    HISTORICAL = "historical"
    STATIC = "static"
    MODELLED = "modelled"


class AcquisitionMode(str, Enum):
    """Acquisition modes - PRD Section 3"""
    REST_API = "rest_api"
    SCIENTIFIC_SERVICE = "erddap"  # ERDDAP, OGC, STAC, OPeNDAP
    SDK = "sdk"
    DOWNLOAD = "download"
    WEB_FALLBACK = "web_fallback"


@dataclass
class SourceMetadata:
    """Source metadata for registry"""
    source_id: str
    provider: str
    name: str
    interface_type: AcquisitionMode
    capabilities: List[str]  # Methods this adapter supports
    endpoint_verified: bool
    base_url: Optional[str] = None
    auth_required: bool = False
    variables: List[str] = None
    coverage: Optional[str] = None


@dataclass
class Payload:
    """Normalized data payload"""
    source_id: str
    dataset_id: Optional[str]
    variable: str
    value: float
    unit: str
    latitude: float
    longitude: float
    observed_at: Optional[datetime]
    valid_from: Optional[datetime]
    valid_until: Optional[datetime]
    source_updated_at: Optional[datetime]
    retrieved_at: datetime
    data_type: DataType
    quality_flag: Optional[str] = "good"
    processing_version: Optional[str] = None
    provenance_url: Optional[str] = None
    confidence: float = 0.85


@dataclass
class HealthStatus:
    """Health check result"""
    ok: bool
    latency_ms: int
    error_code: Optional[str] = None
    detail: Optional[str] = None


@dataclass
class SpatialQuery:
    """Spatial query parameters"""
    latitude: float
    longitude: float
    radius_km: Optional[float] = 50.0


@dataclass
class SpatioTemporalQuery(SpatialQuery):
    """Spatio-temporal query parameters"""
    time_start: Optional[datetime] = None
    time_end: Optional[datetime] = None


@dataclass
class SubsetQuery(SpatioTemporalQuery):
    """Dataset subset query"""
    dataset_id: Optional[str] = None
    variables: Optional[List[str]] = None


class SourceAdapter(ABC):
    """
    Base class for all source adapters
    PRD Section 3.1, 4.1
    
    Adapters expose ONLY the methods their source actually supports.
    Unsupported methods raise CapabilityNotSupported.
    """
    
    def __init__(self, timeout: int = 10, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
    
    @abstractmethod
    def get_metadata(self) -> SourceMetadata:
        """Return source metadata and capabilities"""
        pass
    
    @abstractmethod
    def health_check(self) -> HealthStatus:
        """Reachability + auth + sample query"""
        pass
    
    def get_latest(self, q: SpatialQuery) -> Payload:
        """Most recent obs/NRT - override if supported"""
        raise CapabilityNotSupported(f"{self.__class__.__name__} does not support get_latest")
    
    def get_forecast(self, q: SpatioTemporalQuery) -> Payload:
        """Forecast data - override if supported"""
        raise CapabilityNotSupported(f"{self.__class__.__name__} does not support get_forecast")
    
    def get_historical(self, q: SpatioTemporalQuery) -> Payload:
        """Historical data - override if supported"""
        raise CapabilityNotSupported(f"{self.__class__.__name__} does not support get_historical")
    
    def get_subset(self, q: SubsetQuery) -> List[Payload]:
        """Variable/time/lat/lon slicing - override if supported"""
        raise CapabilityNotSupported(f"{self.__class__.__name__} does not support get_subset")
    
    def get_warnings(self, q: SpatialQuery) -> List[Dict[str, Any]]:
        """Alerts/advisories - override if supported"""
        raise CapabilityNotSupported(f"{self.__class__.__name__} does not support get_warnings")
    
    def get_status(self) -> Dict[str, Any]:
        """Provider-side status - override if supported"""
        raise CapabilityNotSupported(f"{self.__class__.__name__} does not support get_status")


class CapabilityNotSupported(Exception):
    """Raised when adapter doesn't support a method"""
    pass
