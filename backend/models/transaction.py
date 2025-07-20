from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Enum, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    MATCHED = "matched"
    PARTIAL_MATCH = "partial_match"
    EXCEPTION = "exception"
    MISSING = "missing"


class ReconciliationStatus(str, enum.Enum):
    AUTO_MATCHED = "auto_matched"
    MANUALLY_MATCHED = "manually_matched"
    EXCEPTION = "exception"
    UNDER_REVIEW = "under_review"


class BankTransaction(Base):
    __tablename__ = "bank_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_date = Column(DateTime, nullable=False, index=True)
    amount = Column(Numeric(15, 2), nullable=False)
    reference_number = Column(String, index=True)
    description = Column(Text)
    card_type = Column(String)
    terminal_id = Column(String, index=True)
    bank_name = Column(String)
    merchant_name = Column(String)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reconciliation_records = relationship("ReconciliationRecord", back_populates="bank_transaction")


class POSTransaction(Base):
    __tablename__ = "pos_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_date = Column(DateTime, nullable=False, index=True)
    amount = Column(Numeric(15, 2), nullable=False)
    reference_number = Column(String, index=True)
    terminal_id = Column(String, ForeignKey("pos_terminals.terminal_id"), index=True)
    card_type = Column(String)
    merchant_name = Column(String)
    batch_number = Column(String)
    receipt_number = Column(String)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    terminal = relationship("POSTerminal", back_populates="pos_transactions")
    reconciliation_records = relationship("ReconciliationRecord", back_populates="pos_transaction")


class ReconciliationRecord(Base):
    __tablename__ = "reconciliation_records"
    
    id = Column(Integer, primary_key=True, index=True)
    pos_transaction_id = Column(Integer, ForeignKey("pos_transactions.id"))
    bank_transaction_id = Column(Integer, ForeignKey("bank_transactions.id"))
    reconciliation_status = Column(Enum(ReconciliationStatus), nullable=False)
    match_confidence = Column(Numeric(5, 2))  # AI confidence score 0-100
    amount_difference = Column(Numeric(15, 2))
    date_difference_hours = Column(Integer)  # Hours difference between transactions
    reconciled_by = Column(Integer, ForeignKey("users.id"))
    reconciled_at = Column(DateTime, default=datetime.utcnow)
    comments = Column(Text)
    exception_reason = Column(String)
    is_split_transaction = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    pos_transaction = relationship("POSTransaction", back_populates="reconciliation_records")
    bank_transaction = relationship("BankTransaction", back_populates="reconciliation_records")
    reconciled_by_user = relationship("User")