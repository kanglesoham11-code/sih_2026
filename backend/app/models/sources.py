"""
Source Registry, Credentials Metadata, and Health models
PRD Section 27.2 - Source Governance
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.models.base import Base


class SourceRegistry(Base):
    """
    Source Registry - PRD Section 28
    Tracks all data sources with their capabilities and status
    """
    
    __tablename__ = "source_registry"
    
    source_id = Column(String(100), primary_key=True)  # e.g., 'incois_erddap'
    provider = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    interface_type = Column(String(50), nullable=False)  # rest_api|erddap|ogc|sdk|download|web_fallback
    base_url = Column(Text)
    auth_type = Column(String(50), nullable=False)  # none|api_key|basic|token|account|unknown_pending_verification
    credential_env_vars = Column(ARRAY(String))  # Names only, NEVER values
    coverage = Column(Text)
    variables = Column(ARRAY(String))
    update_frequency = Column(String(100))
    expected_latency = Column(String(100))
    freshness_policy = Column(JSONB)  # {"class": "high", "max_age_s": 900}
    license = Column(Text)
    attribution = Column(Text)
    terms_url = Column(Text)
    status = Column(String(50), nullable=False, default="inactive")
    last_success = Column(DateTime)
    last_failure = Column(DateTime)
    last_source_update = Column(DateTime)
    last_retrieved = Column(DateTime)
    endpoint_verified = Column(Boolean, nullable=False, default=False)
    notes = Column(Text)
    
    # Relationships
    health_checks = relationship("SourceHealth", back_populates="source", cascade="all, delete-orphan")
    datasets = relationship("Dataset", back_populates="source")
    
    def __repr__(self):
        return f"<SourceRegistry {self.source_id} ({self.provider})>"


class SourceCredentialsMetadata(Base):
    """
    Credential metadata ONLY - NEVER stores actual secrets
    PRD Section 27.2
    """
    
    __tablename__ = "source_credentials_metadata"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(String(100), ForeignKey("source_registry.source_id"), nullable=False)
    credential_name = Column(String(255), nullable=False)  # env var / secret-manager key name
    requirement = Column(String(50), nullable=False)  # required|optional|unknown_until_verified
    rotation_period_days = Column(Integer)
    last_rotated_at = Column(DateTime)
    stored_in = Column(String(50), nullable=False, default="secret_manager")
    
    def __repr__(self):
        return f"<CredentialMetadata {self.credential_name} for {self.source_id}>"


class SourceHealth(Base):
    """
    Source health check history
    PRD Section 27.2
    """
    
    __tablename__ = "source_health"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    source_id = Column(String(100), ForeignKey("source_registry.source_id"), nullable=False, index=True)
    checked_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    ok = Column(Boolean, nullable=False)
    latency_ms = Column(Integer)
    error_code = Column(String(50))  # PRD Section 18.2 taxonomy
    detail = Column(Text)
    
    # Relationships
    source = relationship("SourceRegistry", back_populates="health_checks")
    
    def __repr__(self):
        return f"<SourceHealth {self.source_id} at {self.checked_at}: {'OK' if self.ok else 'FAIL'}>"
