from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class POSTerminal(Base):
    __tablename__ = "pos_terminals"
    
    id = Column(Integer, primary_key=True, index=True)
    terminal_name = Column(String, nullable=False)
    terminal_id = Column(String, unique=True, index=True, nullable=False)  # TID
    trsm = Column(String)  # Terminal Routing Serial Number
    user_name = Column(String)
    user_phone = Column(String)
    branch = Column(String)
    merchant_name = Column(String, nullable=False)
    bank = Column(String)
    device_type = Column(String)
    mcc_code = Column(String)  # Merchant Category Code
    last_transaction_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    pos_transactions = relationship("POSTransaction", back_populates="terminal")