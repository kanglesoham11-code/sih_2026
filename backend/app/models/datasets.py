"""
Dataset and Dataset Variable models
PRD Section 27.2 - ERDDAP Dataset Registry
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from app.models.base import Base


class Dataset(Base):
    """
    Dataset Registry - PRD Section 5.3
    Tracks ERDDAP and other datasets
    """
    
    __tablename__ = "datasets"
    
    dataset_id = Column(String(100), primary_key=True)  # e.g., 'incois_oceansat2_datasets'
    source_id = Column(String(100), ForeignKey("source_registry.source_id"), nullable=False, index=True)
    title = Column(Text)
    spatial_coverage = Column(Geometry(geometry_type="POLYGON", srid=4326))
    temporal_start = Column(DateTime)
    temporal_end = Column(DateTime)  # Last available source time
    last_retrieved = Column(DateTime)
    update_frequency = Column(String(100))
    freshness_class = Column(String(50))  # critical|high|medium|low|static
    data_type_flag = Column(String(50), nullable=False)  # live|nrt|forecast|historical|static
    access_url = Column(Text)
    response_formats = Column(ARRAY(String))
    auth_required = Column(Boolean)
    quality_metadata = Column(JSONB)
    status = Column(String(50), nullable=False, default="unverified")
    
    # Relationships
    source = relationship("SourceRegistry", back_populates="datasets")
    variables = relationship("DatasetVariable", back_populates="dataset", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Dataset {self.dataset_id} ({self.data_type_flag})>"


class DatasetVariable(Base):
    """
    Variables within a dataset
    """
    
    __tablename__ = "dataset_variables"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    dataset_id = Column(String(100), ForeignKey("datasets.dataset_id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)  # CHL, KD490, TSM, etc.
    standard_name = Column(String(255))
    unit = Column(String(50))
    valid_min = Column(String(50))  # Stored as string for flexibility
    valid_max = Column(String(50))
    missing_value_encoding = Column(String(100))
    
    # Relationships
    dataset = relationship("Dataset", back_populates="variables")
    
    def __repr__(self):
        return f"<DatasetVariable {self.name} in {self.dataset_id}>"
