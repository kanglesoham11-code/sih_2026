"""
Static geospatial layers - boundaries, protected areas, bathymetry
PRD Section 27.2 - Static Versioned Layers
"""

from sqlalchemy import Column, String, Text, DateTime, BigInteger
from geoalchemy2 import Geometry, Raster

from app.models.base import Base


class MarineBoundary(Base):
    """
    Maritime boundaries (EEZ, territorial waters, etc.)
    Source: Marine Regions
    """
    
    __tablename__ = "marine_boundaries"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    boundary_type = Column(String(100), nullable=False)  # eez|territorial_12nm|contiguous|...
    name = Column(Text)
    geom = Column(Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=False, index=True)
    source_version = Column(String(100), nullable=False)  # e.g., 'World EEZ v12'
    ingested_at = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<MarineBoundary {self.boundary_type}: {self.name}>"


class ProtectedArea(Base):
    """
    Protected marine areas
    Source: Protected Planet / WDPA
    """
    
    __tablename__ = "protected_areas"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    wdpa_id = Column(BigInteger)
    name = Column(Text)
    designation = Column(String(255))
    geom = Column(Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=False, index=True)
    source_version = Column(String(100), nullable=False)
    license_note = Column(Text)
    ingested_at = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<ProtectedArea {self.name}>"


class Bathymetry(Base):
    """
    Bathymetry raster data
    Source: GEBCO
    """
    
    __tablename__ = "bathymetry"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    region = Column(String(100), nullable=False)
    rast = Column(Raster)  # PostGIS raster type
    grid_version = Column(String(50), nullable=False)  # 'GEBCO_2026'
    ingested_at = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<Bathymetry {self.region} ({self.grid_version})>"
