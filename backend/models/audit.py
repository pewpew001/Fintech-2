from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)  # e.g., "RECONCILE", "UPLOAD", "MATCH"
    entity_type = Column(String)  # e.g., "reconciliation_record", "pos_transaction"
    entity_id = Column(Integer)
    old_values = Column(JSON)  # Store previous state
    new_values = Column(JSON)  # Store new state
    ip_address = Column(String)
    user_agent = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    session_id = Column(String)
    comments = Column(Text)
    
    # Relationships
    user = relationship("User")