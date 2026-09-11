"""
Recommendations, Routes, and Evidence models
PRD Section 27.2
"""

import uuid
from sqlalchemy import Column, String, Text, DateTime, Float, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from app.models.base import Base


class Recommendation(Base):
    """
    Answer/recommendation provided to user
    """
    
    __tablename__ = "recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"))
    kind = Column(String(100), nullable=False)  # fishing_zone|route|conditions|event_status|...
    summary = Column(Text, nullable=False)
    risk_class = Column(String(50))  # safe|caution|unsafe|no_go
    confidence = Column(Float)
    query_mode = Column(String(20), nullable=False)  # standard|live
    created_at = Column(DateTime, nullable=False)
    
    # Relationships
    routes = relationship("Route", back_populates="recommendation", cascade="all, delete-orphan")
    evidence = relationship("Evidence", back_populates="recommendation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Recommendation {self.kind} ({self.risk_class})>"


class Route(Base):
    """
    Computed safe route
    PRD Section 1.2 UC-5
    """
    
    __tablename__ = "routes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recommendation_id = Column(UUID(as_uuid=True), ForeignKey("recommendations.id"))
    geom = Column(Geometry(geometry_type="LINESTRING", srid=4326), nullable=False)
    distance_m = Column(Float)
    est_duration_s = Column(Integer)
    risk_score = Column(Float)
    segment_risks = Column(JSONB)
    constraints_applied = Column(JSONB)
    created_at = Column(DateTime, nullable=False)
    
    # Relationships
    recommendation = relationship("Recommendation", back_populates="routes")
    
    def __repr__(self):
        return f"<Route {self.distance_m}m, risk={self.risk_score}>"


class Evidence(Base):
    """
    Evidence supporting a recommendation
    PRD Section 0.3 #16 - Full provenance
    """
    
    __tablename__ = "evidence"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recommendation_id = Column(UUID(as_uuid=True), ForeignKey("recommendations.id"), nullable=False, index=True)
    claim = Column(Text, nullable=False)
    source_id = Column(String(100), nullable=False)
    dataset_id = Column(String(100))
    variable = Column(String(100))
    value_ref = Column(JSONB)  # Canonical item snapshot
    observed_at = Column(DateTime)
    valid_time = Column(DateTime)
    retrieved_at = Column(DateTime)
    provenance_id = Column(UUID(as_uuid=True))
    processing_step = Column(String(100))
    confidence = Column(Float)
    
    # Relationships
    recommendation = relationship("Recommendation", back_populates="evidence")
    
    def __repr__(self):
        return f"<Evidence for {self.recommendation_id}: {self.claim[:50]}>"
