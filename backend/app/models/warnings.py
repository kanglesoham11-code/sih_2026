"""
Warning/Alert model
PRD Section 27.2
"""

import uuid
from sqlalchemy import Column, String, Text, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry

from app.models.base import Base


class Warning(Base):
    """
    Marine warnings and alerts
    PRD Section 10.2 - CRITICAL mode
    """
    
    __tablename__ = "warnings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(String(100), nullable=False, index=True)
    warning_type = Column(String(100), nullable=False)  # cyclone|high_wave|lightning|...
    severity = Column(String(50))
    area = Column(Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=False, index=True)
    issued_at = Column(DateTime, nullable=False)
    valid_from = Column(DateTime)
    valid_until = Column(DateTime, index=True)
    retrieved_at = Column(DateTime, nullable=False)
    text = Column(Text)
    provenance_id = Column(UUID(as_uuid=True))
    active = Column(Boolean, nullable=False, default=True, index=True)
    
    def __repr__(self):
        return f"<Warning {self.warning_type} ({self.severity}) issued {self.issued_at}>"
