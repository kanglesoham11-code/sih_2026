"""
Potential Fishing Zone (PFZ) model
"""

import uuid
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from geoalchemy2 import Geometry

from app.models.base import Base


class PFZZone(Base):
    """
    Potential Fishing Zones from INCOIS
    PRD Section 1.2 UC-1, UC-2
    """
    
    __tablename__ = "pfz_zones"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(String(100), nullable=False)
    advisory_id = Column(String(100))
    sector = Column(String(100))
    geom = Column(Geometry(geometry_type="GEOMETRY", srid=4326), nullable=False, index=True)  # Line or polygon
    issued_at = Column(DateTime)
    valid_until = Column(DateTime)
    retrieved_at = Column(DateTime, nullable=False)
    attributes = Column(JSONB)  # Additional PFZ attributes
    provenance_id = Column(UUID(as_uuid=True))
    
    def __repr__(self):
        return f"<PFZZone {self.sector} issued {self.issued_at}>"
