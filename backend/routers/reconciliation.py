from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from ..database import get_db
from ..models.user import User
from ..models.transaction import ReconciliationRecord, TransactionStatus
from ..schemas.transaction import (
    ReconciliationRecordResponse, ReconciliationRecordCreate,
    TransactionSummary
)
from ..services.auth import get_current_active_user
from ..services.reconciliation_engine import ReconciliationEngine

router = APIRouter()


@router.post("/auto-reconcile")
def auto_reconcile_transactions(
    date_from: date,
    date_to: date,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Perform automatic reconciliation for a date range"""
    
    # Convert dates to datetime for the engine
    date_from_dt = datetime.combine(date_from, datetime.min.time())
    date_to_dt = datetime.combine(date_to, datetime.max.time())
    
    engine = ReconciliationEngine(db)
    result = engine.auto_reconcile_batch(current_user.id, date_from_dt, date_to_dt)
    
    return {
        "message": "Auto-reconciliation completed",
        "results": result
    }


@router.post("/manual-match", response_model=ReconciliationRecordResponse)
def manual_match_transactions(
    pos_transaction_id: int,
    bank_transaction_id: int,
    comments: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Manually match a POS transaction with a bank transaction"""
    
    try:
        engine = ReconciliationEngine(db)
        reconciliation = engine.manual_match(
            current_user.id, pos_transaction_id, bank_transaction_id, comments
        )
        return reconciliation
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/mark-exception", response_model=ReconciliationRecordResponse)
def mark_transaction_exception(
    transaction_id: int,
    transaction_type: str,  # "pos" or "bank"
    reason: str,
    comments: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark a transaction as an exception"""
    
    if transaction_type.lower() not in ["pos", "bank"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction type must be 'pos' or 'bank'"
        )
    
    try:
        engine = ReconciliationEngine(db)
        reconciliation = engine.mark_exception(
            current_user.id, transaction_id, transaction_type, reason, comments
        )
        return reconciliation
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/records", response_model=List[ReconciliationRecordResponse])
def get_reconciliation_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get reconciliation records with filtering"""
    
    query = db.query(ReconciliationRecord)
    
    if date_from:
        query = query.filter(ReconciliationRecord.reconciled_at >= datetime.combine(date_from, datetime.min.time()))
    
    if date_to:
        query = query.filter(ReconciliationRecord.reconciled_at <= datetime.combine(date_to, datetime.max.time()))
    
    if status:
        query = query.filter(ReconciliationRecord.reconciliation_status == status)
    
    records = query.offset(skip).limit(limit).all()
    return records


@router.get("/summary", response_model=TransactionSummary)
def get_reconciliation_summary(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get reconciliation summary statistics"""
    
    from ..models.transaction import BankTransaction, POSTransaction
    from sqlalchemy import func
    
    # Base queries
    pos_query = db.query(POSTransaction)
    bank_query = db.query(BankTransaction)
    reconciliation_query = db.query(ReconciliationRecord)
    
    # Apply date filters
    if date_from:
        date_from_dt = datetime.combine(date_from, datetime.min.time())
        pos_query = pos_query.filter(POSTransaction.transaction_date >= date_from_dt)
        bank_query = bank_query.filter(BankTransaction.transaction_date >= date_from_dt)
        reconciliation_query = reconciliation_query.filter(ReconciliationRecord.reconciled_at >= date_from_dt)
    
    if date_to:
        date_to_dt = datetime.combine(date_to, datetime.max.time())
        pos_query = pos_query.filter(POSTransaction.transaction_date <= date_to_dt)
        bank_query = bank_query.filter(BankTransaction.transaction_date <= date_to_dt)
        reconciliation_query = reconciliation_query.filter(ReconciliationRecord.reconciled_at <= date_to_dt)
    
    # Get counts
    total_pos = pos_query.count()
    total_bank = bank_query.count()
    matched_pos = pos_query.filter(POSTransaction.status == TransactionStatus.MATCHED).count()
    matched_bank = bank_query.filter(BankTransaction.status == TransactionStatus.MATCHED).count()
    exceptions = reconciliation_query.filter(ReconciliationRecord.reconciliation_status == "exception").count()
    
    # Get amounts
    pos_amount = pos_query.with_entities(func.sum(POSTransaction.amount)).scalar() or 0
    bank_amount = bank_query.with_entities(func.sum(BankTransaction.amount)).scalar() or 0
    matched_pos_amount = pos_query.filter(POSTransaction.status == TransactionStatus.MATCHED).with_entities(func.sum(POSTransaction.amount)).scalar() or 0
    
    return TransactionSummary(
        total_pos_transactions=total_pos,
        total_bank_transactions=total_bank,
        matched_transactions=min(matched_pos, matched_bank),
        unmatched_pos=total_pos - matched_pos,
        unmatched_bank=total_bank - matched_bank,
        exceptions=exceptions,
        total_pos_amount=pos_amount,
        total_bank_amount=bank_amount,
        matched_amount=matched_pos_amount,
        variance_amount=abs(pos_amount - bank_amount)
    )


@router.delete("/records/{record_id}")
def delete_reconciliation_record(
    record_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a reconciliation record (undo reconciliation)"""
    
    # Check user permissions (only admin or the user who created it)
    record = db.query(ReconciliationRecord).filter(ReconciliationRecord.id == record_id).first()
    
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reconciliation record not found")
    
    if current_user.role != "admin" and record.reconciled_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this record")
    
    # Reset transaction statuses
    if record.pos_transaction:
        record.pos_transaction.status = TransactionStatus.PENDING
    
    if record.bank_transaction:
        record.bank_transaction.status = TransactionStatus.PENDING
    
    # Delete the record
    db.delete(record)
    db.commit()
    
    return {"message": "Reconciliation record deleted successfully"}