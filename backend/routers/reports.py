from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import Optional
from datetime import date, datetime
import pandas as pd
import io

from ..database import get_db
from ..models.user import User
from ..models.transaction import BankTransaction, POSTransaction, ReconciliationRecord, TransactionStatus
from ..models.pos_terminal import POSTerminal
from ..services.auth import get_current_active_user

router = APIRouter()


@router.get("/reconciliation-summary")
def get_reconciliation_summary_report(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    format: str = Query("json", regex="^(json|csv|excel)$"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate reconciliation summary report"""
    
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
    
    # Calculate summary statistics
    summary = {
        "period": {
            "from": date_from.isoformat() if date_from else None,
            "to": date_to.isoformat() if date_to else None
        },
        "transactions": {
            "total_pos": pos_query.count(),
            "total_bank": bank_query.count(),
            "matched_pos": pos_query.filter(POSTransaction.status == TransactionStatus.MATCHED).count(),
            "matched_bank": bank_query.filter(BankTransaction.status == TransactionStatus.MATCHED).count(),
            "pending_pos": pos_query.filter(POSTransaction.status == TransactionStatus.PENDING).count(),
            "pending_bank": bank_query.filter(BankTransaction.status == TransactionStatus.PENDING).count(),
            "exceptions": reconciliation_query.filter(ReconciliationRecord.reconciliation_status == "exception").count()
        },
        "amounts": {
            "total_pos_amount": float(pos_query.with_entities(func.sum(POSTransaction.amount)).scalar() or 0),
            "total_bank_amount": float(bank_query.with_entities(func.sum(BankTransaction.amount)).scalar() or 0),
            "matched_pos_amount": float(pos_query.filter(POSTransaction.status == TransactionStatus.MATCHED).with_entities(func.sum(POSTransaction.amount)).scalar() or 0),
            "matched_bank_amount": float(bank_query.filter(BankTransaction.status == TransactionStatus.MATCHED).with_entities(func.sum(BankTransaction.amount)).scalar() or 0)
        }
    }
    
    # Calculate reconciliation rate
    if summary["transactions"]["total_pos"] > 0:
        summary["reconciliation_rate"] = round(
            (summary["transactions"]["matched_pos"] / summary["transactions"]["total_pos"]) * 100, 2
        )
    else:
        summary["reconciliation_rate"] = 0
    
    if format == "json":
        return summary
    
    # Convert to DataFrame for CSV/Excel export
    df = pd.DataFrame([
        {"Metric": "Total POS Transactions", "Value": summary["transactions"]["total_pos"]},
        {"Metric": "Total Bank Transactions", "Value": summary["transactions"]["total_bank"]},
        {"Metric": "Matched POS Transactions", "Value": summary["transactions"]["matched_pos"]},
        {"Metric": "Matched Bank Transactions", "Value": summary["transactions"]["matched_bank"]},
        {"Metric": "Pending POS Transactions", "Value": summary["transactions"]["pending_pos"]},
        {"Metric": "Pending Bank Transactions", "Value": summary["transactions"]["pending_bank"]},
        {"Metric": "Exception Records", "Value": summary["transactions"]["exceptions"]},
        {"Metric": "Total POS Amount", "Value": summary["amounts"]["total_pos_amount"]},
        {"Metric": "Total Bank Amount", "Value": summary["amounts"]["total_bank_amount"]},
        {"Metric": "Matched POS Amount", "Value": summary["amounts"]["matched_pos_amount"]},
        {"Metric": "Matched Bank Amount", "Value": summary["amounts"]["matched_bank_amount"]},
        {"Metric": "Reconciliation Rate (%)", "Value": summary["reconciliation_rate"]}
    ])
    
    if format == "csv":
        csv_content = df.to_csv(index=False)
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=reconciliation_summary.csv"}
        )
    
    elif format == "excel":
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False, sheet_name="Reconciliation Summary")
        excel_buffer.seek(0)
        
        return Response(
            content=excel_buffer.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=reconciliation_summary.xlsx"}
        )


@router.get("/detailed-reconciliation")
def get_detailed_reconciliation_report(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    format: str = Query("json", regex="^(json|csv|excel)$"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate detailed reconciliation report"""
    
    # Get reconciliation records with related transactions
    query = db.query(ReconciliationRecord).join(
        POSTransaction, ReconciliationRecord.pos_transaction_id == POSTransaction.id, isouter=True
    ).join(
        BankTransaction, ReconciliationRecord.bank_transaction_id == BankTransaction.id, isouter=True
    )
    
    if date_from:
        query = query.filter(ReconciliationRecord.reconciled_at >= datetime.combine(date_from, datetime.min.time()))
    
    if date_to:
        query = query.filter(ReconciliationRecord.reconciled_at <= datetime.combine(date_to, datetime.max.time()))
    
    records = query.all()
    
    detailed_data = []
    for record in records:
        row = {
            "reconciliation_id": record.id,
            "reconciliation_status": record.reconciliation_status.value,
            "match_confidence": float(record.match_confidence) if record.match_confidence else None,
            "amount_difference": float(record.amount_difference) if record.amount_difference else None,
            "date_difference_hours": record.date_difference_hours,
            "reconciled_at": record.reconciled_at.isoformat(),
            "comments": record.comments,
            "exception_reason": record.exception_reason,
            "pos_transaction_id": record.pos_transaction_id,
            "pos_amount": float(record.pos_transaction.amount) if record.pos_transaction else None,
            "pos_date": record.pos_transaction.transaction_date.isoformat() if record.pos_transaction else None,
            "pos_terminal_id": record.pos_transaction.terminal_id if record.pos_transaction else None,
            "bank_transaction_id": record.bank_transaction_id,
            "bank_amount": float(record.bank_transaction.amount) if record.bank_transaction else None,
            "bank_date": record.bank_transaction.transaction_date.isoformat() if record.bank_transaction else None,
            "bank_reference": record.bank_transaction.reference_number if record.bank_transaction else None
        }
        detailed_data.append(row)
    
    if format == "json":
        return {"reconciliation_records": detailed_data}
    
    # Convert to DataFrame for export
    df = pd.DataFrame(detailed_data)
    
    if format == "csv":
        csv_content = df.to_csv(index=False)
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=detailed_reconciliation.csv"}
        )
    
    elif format == "excel":
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False, sheet_name="Detailed Reconciliation")
        excel_buffer.seek(0)
        
        return Response(
            content=excel_buffer.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=detailed_reconciliation.xlsx"}
        )


@router.get("/terminal-performance")
def get_terminal_performance_report(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    format: str = Query("json", regex="^(json|csv|excel)$"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate terminal performance report"""
    
    # Get terminal performance data
    query = db.query(
        POSTerminal.terminal_id,
        POSTerminal.terminal_name,
        POSTerminal.merchant_name,
        POSTerminal.branch,
        POSTerminal.bank,
        func.count(POSTransaction.id).label('total_transactions'),
        func.sum(POSTransaction.amount).label('total_amount'),
        func.count(
            case([(POSTransaction.status == TransactionStatus.MATCHED, 1)])
        ).label('matched_transactions'),
        func.sum(
            case([(POSTransaction.status == TransactionStatus.MATCHED, POSTransaction.amount)], else_=0)
        ).label('matched_amount')
    ).join(
        POSTransaction, POSTerminal.terminal_id == POSTransaction.terminal_id
    ).group_by(
        POSTerminal.terminal_id,
        POSTerminal.terminal_name,
        POSTerminal.merchant_name,
        POSTerminal.branch,
        POSTerminal.bank
    )
    
    if date_from:
        query = query.filter(POSTransaction.transaction_date >= datetime.combine(date_from, datetime.min.time()))
    
    if date_to:
        query = query.filter(POSTransaction.transaction_date <= datetime.combine(date_to, datetime.max.time()))
    
    results = query.all()
    
    performance_data = []
    for result in results:
        reconciliation_rate = 0
        if result.total_transactions > 0:
            reconciliation_rate = round((result.matched_transactions / result.total_transactions) * 100, 2)
        
        performance_data.append({
            "terminal_id": result.terminal_id,
            "terminal_name": result.terminal_name,
            "merchant_name": result.merchant_name,
            "branch": result.branch,
            "bank": result.bank,
            "total_transactions": result.total_transactions,
            "total_amount": float(result.total_amount or 0),
            "matched_transactions": result.matched_transactions,
            "matched_amount": float(result.matched_amount or 0),
            "reconciliation_rate": reconciliation_rate
        })
    
    if format == "json":
        return {"terminal_performance": performance_data}
    
    # Convert to DataFrame for export
    df = pd.DataFrame(performance_data)
    
    if format == "csv":
        csv_content = df.to_csv(index=False)
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=terminal_performance.csv"}
        )
    
    elif format == "excel":
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False, sheet_name="Terminal Performance")
        excel_buffer.seek(0)
        
        return Response(
            content=excel_buffer.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=terminal_performance.xlsx"}
        )


@router.get("/exceptions-report")
def get_exceptions_report(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    format: str = Query("json", regex="^(json|csv|excel)$"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate exceptions report"""
    
    # Get exception records
    query = db.query(ReconciliationRecord).filter(
        ReconciliationRecord.reconciliation_status == "exception"
    )
    
    if date_from:
        query = query.filter(ReconciliationRecord.reconciled_at >= datetime.combine(date_from, datetime.min.time()))
    
    if date_to:
        query = query.filter(ReconciliationRecord.reconciled_at <= datetime.combine(date_to, datetime.max.time()))
    
    exceptions = query.all()
    
    exceptions_data = []
    for exception in exceptions:
        row = {
            "exception_id": exception.id,
            "reconciled_at": exception.reconciled_at.isoformat(),
            "exception_reason": exception.exception_reason,
            "comments": exception.comments,
            "pos_transaction_id": exception.pos_transaction_id,
            "bank_transaction_id": exception.bank_transaction_id
        }
        
        # Add transaction details
        if exception.pos_transaction:
            row.update({
                "pos_amount": float(exception.pos_transaction.amount),
                "pos_date": exception.pos_transaction.transaction_date.isoformat(),
                "pos_terminal_id": exception.pos_transaction.terminal_id,
                "pos_reference": exception.pos_transaction.reference_number
            })
        
        if exception.bank_transaction:
            row.update({
                "bank_amount": float(exception.bank_transaction.amount),
                "bank_date": exception.bank_transaction.transaction_date.isoformat(),
                "bank_reference": exception.bank_transaction.reference_number,
                "bank_description": exception.bank_transaction.description
            })
        
        exceptions_data.append(row)
    
    if format == "json":
        return {"exceptions": exceptions_data}
    
    # Convert to DataFrame for export
    df = pd.DataFrame(exceptions_data)
    
    if format == "csv":
        csv_content = df.to_csv(index=False)
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=exceptions_report.csv"}
        )
    
    elif format == "excel":
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False, sheet_name="Exceptions Report")
        excel_buffer.seek(0)
        
        return Response(
            content=excel_buffer.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=exceptions_report.xlsx"}
        )