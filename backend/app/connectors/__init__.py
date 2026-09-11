"""
ORCA Data Connectors
PRD Section 4 - ORCA Data Gateway
"""

from app.connectors.base import SourceAdapter, SourceMetadata, Payload
from app.connectors.incois_erddap import INCOISERDDAPAdapter
from app.connectors.imd_weather import IMDWeatherAdapter
from app.connectors.copernicus_marine import CopernicusMarineAdapter

__all__ = [
    "SourceAdapter",
    "SourceMetadata",
    "Payload",
    "INCOISERDDAPAdapter",
    "IMDWeatherAdapter",
    "CopernicusMarineAdapter",
]
