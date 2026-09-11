"""
Audit log model
"""

from sqlalchemy import Column, String, Text, DateTime, BigInteger
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime

from app.models.base import Base


class AuditLog(Base):
    """
    Audit trail for admin actions
    PRD Section 23 - Security
    """
    
    __tablename__ = "audit_logs"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    actor = Column(UUID(as_uuid=True))
    action = Column(String(100), nullable=False)
    target = Column(String(255))
    detail = Column(JSONB)
    at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<AuditLog {self.action} by {self.actor} at {self.at}>"
