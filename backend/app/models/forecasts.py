"""
Forecast data model
PRD Section 27.2
"""

from sqlalchemy import Column, String, Text, DateTime, BigInteger, Float
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry

from app.models.base import Base


class Forecast(Base):
    """
    Forecast data - separate from observations
    PRD Section 31 - Data-Type Labels
    """
    
    __tablename__ = "forecasts"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    source_id = Column(String(100), nullable=False, index=True)
    dataset_id = Column(String(100))
    variable = Column(String(100), nullable=False, index=True)
    value = Column(Float)
    unit = Column(String(50), nullable=False)
    geom = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False, index=True)
    issued_at = Column(DateTime, nullable=False)  # Model cycle time
    valid_from = Column(DateTime, nullable=False, primary_key=True, index=True)
    valid_until = Column(DateTime)
    retrieved_at = Column(DateTime, nullable=False)
    quality_flag = Column(String(50))
    processing_version = Column(String(50))
    provenance_id = Column(UUID(as_uuid=True))
    confidence = Column(Float)
    
    # Note: Partition by RANGE(valid_from)
    
    def __repr__(self):
        return f"<Forecast {self.variable}={self.value}{self.unit} valid from {self.valid_from}>"
