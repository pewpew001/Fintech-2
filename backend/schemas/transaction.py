from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal
from ..models.transaction import TransactionStatus, ReconciliationStatus


class BankTransactionBase(BaseModel):
    transaction_date: datetime
    amount: Decimal
    reference_number: Optional[str] = None
    description: Optional[str] = None
    card_type: Optional[str] = None
    terminal_id: Optional[str] = None
    bank_name: Optional[str] = None
    merchant_name: Optional[str] = None


class BankTransactionCreate(BankTransactionBase):
    pass


class BankTransactionResponse(BankTransactionBase):
    id: int
    status: TransactionStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class POSTransactionBase(BaseModel):
    transaction_date: datetime
    amount: Decimal
    reference_number: Optional[str] = None
    terminal_id: str
    card_type: Optional[str] = None
    merchant_name: Optional[str] = None
    batch_number: Optional[str] = None
    receipt_number: Optional[str] = None


class POSTransactionCreate(POSTransactionBase):
    pass


class POSTransactionResponse(POSTransactionBase):
    id: int
    status: TransactionStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReconciliationRecordBase(BaseModel):
    reconciliation_status: ReconciliationStatus
    comments: Optional[str] = None
    exception_reason: Optional[str] = None
    is_split_transaction: bool = False


class ReconciliationRecordCreate(ReconciliationRecordBase):
    pos_transaction_id: Optional[int] = None
    bank_transaction_id: Optional[int] = None


class ReconciliationRecordResponse(ReconciliationRecordBase):
    id: int
    pos_transaction_id: Optional[int] = None
    bank_transaction_id: Optional[int] = None
    match_confidence: Optional[Decimal] = None
    amount_difference: Optional[Decimal] = None
    date_difference_hours: Optional[int] = None
    reconciled_by: Optional[int] = None
    reconciled_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TransactionSummary(BaseModel):
    total_pos_transactions: int
    total_bank_transactions: int
    matched_transactions: int
    unmatched_pos: int
    unmatched_bank: int
    exceptions: int
    total_pos_amount: Decimal
    total_bank_amount: Decimal
    matched_amount: Decimal
    variance_amount: Decimal