from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime

from ..database import get_db
from ..models.user import User
from ..models.transaction import BankTransaction, POSTransaction, TransactionStatus
from ..schemas.transaction import (
    BankTransactionCreate, BankTransactionResponse,
    POSTransactionCreate, POSTransactionResponse
)
from ..services.auth import get_current_active_user

router = APIRouter()


# POS Transaction endpoints
@router.get("/pos", response_model=List[POSTransactionResponse])
def get_pos_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    terminal_id: Optional[str] = None,
    status: Optional[TransactionStatus] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get POS transactions with filtering"""
    
    query = db.query(POSTransaction)
    
    if date_from:
        query = query.filter(POSTransaction.transaction_date >= datetime.combine(date_from, datetime.min.time()))
    
    if date_to:
        query = query.filter(POSTransaction.transaction_date <= datetime.combine(date_to, datetime.max.time()))
    
    if terminal_id:
        query = query.filter(POSTransaction.terminal_id == terminal_id)
    
    if status:
        query = query.filter(POSTransaction.status == status)
    
    transactions = query.order_by(POSTransaction.transaction_date.desc()).offset(skip).limit(limit).all()
    return transactions


@router.post("/pos", response_model=POSTransactionResponse)
def create_pos_transaction(
    transaction: POSTransactionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new POS transaction"""
    
    db_transaction = POSTransaction(**transaction.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    
    return db_transaction


@router.get("/pos/{transaction_id}", response_model=POSTransactionResponse)
def get_pos_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific POS transaction"""
    
    transaction = db.query(POSTransaction).filter(POSTransaction.id == transaction_id).first()
    
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POS transaction not found")
    
    return transaction


@router.put("/pos/{transaction_id}", response_model=POSTransactionResponse)
def update_pos_transaction(
    transaction_id: int,
    transaction_update: POSTransactionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a POS transaction"""
    
    transaction = db.query(POSTransaction).filter(POSTransaction.id == transaction_id).first()
    
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POS transaction not found")
    
    # Update fields
    for field, value in transaction_update.dict(exclude_unset=True).items():
        setattr(transaction, field, value)
    
    db.commit()
    db.refresh(transaction)
    
    return transaction


@router.delete("/pos/{transaction_id}")
def delete_pos_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a POS transaction"""
    
    transaction = db.query(POSTransaction).filter(POSTransaction.id == transaction_id).first()
    
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POS transaction not found")
    
    # Check if transaction is already reconciled
    if transaction.status == TransactionStatus.MATCHED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a matched transaction. Please undo reconciliation first."
        )
    
    db.delete(transaction)
    db.commit()
    
    return {"message": "POS transaction deleted successfully"}


# Bank Transaction endpoints
@router.get("/bank", response_model=List[BankTransactionResponse])
def get_bank_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    bank_name: Optional[str] = None,
    status: Optional[TransactionStatus] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get bank transactions with filtering"""
    
    query = db.query(BankTransaction)
    
    if date_from:
        query = query.filter(BankTransaction.transaction_date >= datetime.combine(date_from, datetime.min.time()))
    
    if date_to:
        query = query.filter(BankTransaction.transaction_date <= datetime.combine(date_to, datetime.max.time()))
    
    if bank_name:
        query = query.filter(BankTransaction.bank_name.ilike(f"%{bank_name}%"))
    
    if status:
        query = query.filter(BankTransaction.status == status)
    
    transactions = query.order_by(BankTransaction.transaction_date.desc()).offset(skip).limit(limit).all()
    return transactions


@router.post("/bank", response_model=BankTransactionResponse)
def create_bank_transaction(
    transaction: BankTransactionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new bank transaction"""
    
    db_transaction = BankTransaction(**transaction.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    
    return db_transaction


@router.get("/bank/{transaction_id}", response_model=BankTransactionResponse)
def get_bank_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific bank transaction"""
    
    transaction = db.query(BankTransaction).filter(BankTransaction.id == transaction_id).first()
    
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bank transaction not found")
    
    return transaction


@router.put("/bank/{transaction_id}", response_model=BankTransactionResponse)
def update_bank_transaction(
    transaction_id: int,
    transaction_update: BankTransactionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a bank transaction"""
    
    transaction = db.query(BankTransaction).filter(BankTransaction.id == transaction_id).first()
    
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bank transaction not found")
    
    # Update fields
    for field, value in transaction_update.dict(exclude_unset=True).items():
        setattr(transaction, field, value)
    
    db.commit()
    db.refresh(transaction)
    
    return transaction


@router.delete("/bank/{transaction_id}")
def delete_bank_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a bank transaction"""
    
    transaction = db.query(BankTransaction).filter(BankTransaction.id == transaction_id).first()
    
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bank transaction not found")
    
    # Check if transaction is already reconciled
    if transaction.status == TransactionStatus.MATCHED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a matched transaction. Please undo reconciliation first."
        )
    
    db.delete(transaction)
    db.commit()
    
    return {"message": "Bank transaction deleted successfully"}


# Unmatched transactions endpoints
@router.get("/unmatched/pos", response_model=List[POSTransactionResponse])
def get_unmatched_pos_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get unmatched POS transactions"""
    
    transactions = db.query(POSTransaction).filter(
        POSTransaction.status == TransactionStatus.PENDING
    ).order_by(POSTransaction.transaction_date.desc()).offset(skip).limit(limit).all()
    
    return transactions


@router.get("/unmatched/bank", response_model=List[BankTransactionResponse])
def get_unmatched_bank_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get unmatched bank transactions"""
    
    transactions = db.query(BankTransaction).filter(
        BankTransaction.status == TransactionStatus.PENDING
    ).order_by(BankTransaction.transaction_date.desc()).offset(skip).limit(limit).all()
    
    return transactions