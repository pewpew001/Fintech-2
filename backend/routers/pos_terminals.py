from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models.user import User
from ..models.pos_terminal import POSTerminal
from ..schemas.pos_terminal import POSTerminalCreate, POSTerminalUpdate, POSTerminalResponse
from ..services.auth import get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[POSTerminalResponse])
def get_pos_terminals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    branch: Optional[str] = None,
    bank: Optional[str] = None,
    merchant_name: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get POS terminals with filtering"""
    
    query = db.query(POSTerminal)
    
    if branch:
        query = query.filter(POSTerminal.branch.ilike(f"%{branch}%"))
    
    if bank:
        query = query.filter(POSTerminal.bank.ilike(f"%{bank}%"))
    
    if merchant_name:
        query = query.filter(POSTerminal.merchant_name.ilike(f"%{merchant_name}%"))
    
    terminals = query.offset(skip).limit(limit).all()
    return terminals


@router.post("/", response_model=POSTerminalResponse)
def create_pos_terminal(
    terminal: POSTerminalCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new POS terminal"""
    
    # Check if terminal ID already exists
    existing_terminal = db.query(POSTerminal).filter(POSTerminal.terminal_id == terminal.terminal_id).first()
    if existing_terminal:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Terminal ID already exists"
        )
    
    db_terminal = POSTerminal(**terminal.dict())
    db.add(db_terminal)
    db.commit()
    db.refresh(db_terminal)
    
    return db_terminal


@router.get("/{terminal_id}", response_model=POSTerminalResponse)
def get_pos_terminal(
    terminal_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific POS terminal by ID"""
    
    terminal = db.query(POSTerminal).filter(POSTerminal.terminal_id == terminal_id).first()
    
    if not terminal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POS terminal not found")
    
    return terminal


@router.put("/{terminal_id}", response_model=POSTerminalResponse)
def update_pos_terminal(
    terminal_id: str,
    terminal_update: POSTerminalUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a POS terminal"""
    
    terminal = db.query(POSTerminal).filter(POSTerminal.terminal_id == terminal_id).first()
    
    if not terminal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POS terminal not found")
    
    # Update fields
    for field, value in terminal_update.dict(exclude_unset=True).items():
        setattr(terminal, field, value)
    
    db.commit()
    db.refresh(terminal)
    
    return terminal


@router.delete("/{terminal_id}")
def delete_pos_terminal(
    terminal_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a POS terminal"""
    
    # Check user permissions (only admin can delete)
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete terminals")
    
    terminal = db.query(POSTerminal).filter(POSTerminal.terminal_id == terminal_id).first()
    
    if not terminal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POS terminal not found")
    
    db.delete(terminal)
    db.commit()
    
    return {"message": "POS terminal deleted successfully"}


@router.get("/{terminal_id}/transactions")
def get_terminal_transactions(
    terminal_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get transactions for a specific terminal"""
    
    from ..models.transaction import POSTransaction
    
    terminal = db.query(POSTerminal).filter(POSTerminal.terminal_id == terminal_id).first()
    
    if not terminal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POS terminal not found")
    
    transactions = db.query(POSTransaction).filter(
        POSTransaction.terminal_id == terminal_id
    ).order_by(POSTransaction.transaction_date.desc()).offset(skip).limit(limit).all()
    
    return transactions