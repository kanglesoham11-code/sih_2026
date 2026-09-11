"""
Data Observations model
PRD Section 27.2 - Canonical Data
"""

from sqlalchemy import Column, String, Text, DateTime, BigInteger, Float
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry

from app.models.base import Base


class DataObservation(Base):
    """
    Canonical observation data
    PRD Section 11 - Canonical Data Schema
    Partition by retrieved_at for scaling
    """
    
    __tablename__ = "data_observations"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    source_id = Column(String(100), nullable=False, index=True)
    dataset_id = Column(String(100))
    variable = Column(String(100), nullable=False, index=True)
    value = Column(Float)
    unit = Column(String(50), nullable=False)
    geom = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False, index=True)
    observed_at = Column(DateTime, index=True)
    source_updated_at = Column(DateTime)
    retrieved_at = Column(DateTime, nullable=False, primary_key=True, index=True)
    data_type = Column(String(50), nullable=False)  # observation|nrt
    quality_flag = Column(String(50))
    processing_version = Column(String(50))
    provenance_id = Column(UUID(as_uuid=True))
    confidence = Column(Float)
    
    # Note: In production, partition by RANGE(retrieved_at)
    # See PRD Section 27.2 for partitioning strategy
    
    def __repr__(self):
        return f"<DataObservation {self.variable}={self.value}{self.unit} at {self.observed_at}>"
