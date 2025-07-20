from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import pandas as pd
import io
from datetime import datetime

from ..database import get_db
from ..models.user import User
from ..models.transaction import BankTransaction, POSTransaction
from ..schemas.transaction import BankTransactionResponse, POSTransactionResponse
from ..services.auth import get_current_active_user

router = APIRouter()


@router.post("/pos-transactions", response_model=List[POSTransactionResponse])
async def upload_pos_transactions(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload POS transactions from CSV/Excel file"""
    
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be CSV or Excel format"
        )
    
    try:
        contents = await file.read()
        
        # Read file based on extension
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        else:
            df = pd.read_excel(io.BytesIO(contents))
        
        # Expected columns (flexible mapping)
        column_mapping = {
            'transaction_date': ['transaction_date', 'date', 'trans_date', 'Date'],
            'amount': ['amount', 'Amount', 'transaction_amount', 'value'],
            'reference_number': ['reference_number', 'ref_no', 'reference', 'Reference'],
            'terminal_id': ['terminal_id', 'tid', 'Terminal_ID', 'terminal'],
            'card_type': ['card_type', 'Card_Type', 'cardtype'],
            'merchant_name': ['merchant_name', 'merchant', 'Merchant'],
            'batch_number': ['batch_number', 'batch', 'Batch'],
            'receipt_number': ['receipt_number', 'receipt', 'Receipt']
        }
        
        # Map columns
        mapped_columns = {}
        for target_col, possible_names in column_mapping.items():
            for name in possible_names:
                if name in df.columns:
                    mapped_columns[target_col] = name
                    break
        
        # Validate required columns
        required_columns = ['transaction_date', 'amount', 'terminal_id']
        missing_columns = [col for col in required_columns if col not in mapped_columns]
        
        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns: {missing_columns}. Available columns: {list(df.columns)}"
            )
        
        # Process transactions
        created_transactions = []
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Parse date
                date_value = row[mapped_columns['transaction_date']]
                if pd.isna(date_value):
                    continue
                
                if isinstance(date_value, str):
                    transaction_date = pd.to_datetime(date_value)
                else:
                    transaction_date = date_value
                
                # Create transaction
                pos_transaction = POSTransaction(
                    transaction_date=transaction_date,
                    amount=float(row[mapped_columns['amount']]),
                    reference_number=row.get(mapped_columns.get('reference_number', ''), None),
                    terminal_id=str(row[mapped_columns['terminal_id']]),
                    card_type=row.get(mapped_columns.get('card_type', ''), None),
                    merchant_name=row.get(mapped_columns.get('merchant_name', ''), None),
                    batch_number=row.get(mapped_columns.get('batch_number', ''), None),
                    receipt_number=row.get(mapped_columns.get('receipt_number', ''), None)
                )
                
                db.add(pos_transaction)
                created_transactions.append(pos_transaction)
                
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
        
        db.commit()
        
        # Refresh all created transactions
        for txn in created_transactions:
            db.refresh(txn)
        
        result = {
            "message": f"Successfully uploaded {len(created_transactions)} POS transactions",
            "created_count": len(created_transactions),
            "errors": errors,
            "transactions": created_transactions[:10]  # Return first 10 for preview
        }
        
        return created_transactions
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )


@router.post("/bank-transactions", response_model=List[BankTransactionResponse])
async def upload_bank_transactions(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload bank transactions from CSV/Excel file"""
    
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be CSV or Excel format"
        )
    
    try:
        contents = await file.read()
        
        # Read file based on extension
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        else:
            df = pd.read_excel(io.BytesIO(contents))
        
        # Column mapping for bank transactions
        column_mapping = {
            'transaction_date': ['transaction_date', 'date', 'trans_date', 'Date', 'value_date'],
            'amount': ['amount', 'Amount', 'transaction_amount', 'value', 'credit_amount'],
            'reference_number': ['reference_number', 'ref_no', 'reference', 'Reference', 'transaction_ref'],
            'description': ['description', 'Description', 'narration', 'details'],
            'card_type': ['card_type', 'Card_Type', 'cardtype'],
            'terminal_id': ['terminal_id', 'tid', 'Terminal_ID', 'terminal'],
            'bank_name': ['bank_name', 'bank', 'Bank'],
            'merchant_name': ['merchant_name', 'merchant', 'Merchant']
        }
        
        # Map columns
        mapped_columns = {}
        for target_col, possible_names in column_mapping.items():
            for name in possible_names:
                if name in df.columns:
                    mapped_columns[target_col] = name
                    break
        
        # Validate required columns
        required_columns = ['transaction_date', 'amount']
        missing_columns = [col for col in required_columns if col not in mapped_columns]
        
        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns: {missing_columns}. Available columns: {list(df.columns)}"
            )
        
        # Process transactions
        created_transactions = []
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Parse date
                date_value = row[mapped_columns['transaction_date']]
                if pd.isna(date_value):
                    continue
                
                if isinstance(date_value, str):
                    transaction_date = pd.to_datetime(date_value)
                else:
                    transaction_date = date_value
                
                # Create transaction
                bank_transaction = BankTransaction(
                    transaction_date=transaction_date,
                    amount=float(row[mapped_columns['amount']]),
                    reference_number=row.get(mapped_columns.get('reference_number', ''), None),
                    description=row.get(mapped_columns.get('description', ''), None),
                    card_type=row.get(mapped_columns.get('card_type', ''), None),
                    terminal_id=row.get(mapped_columns.get('terminal_id', ''), None),
                    bank_name=row.get(mapped_columns.get('bank_name', ''), None),
                    merchant_name=row.get(mapped_columns.get('merchant_name', ''), None)
                )
                
                db.add(bank_transaction)
                created_transactions.append(bank_transaction)
                
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
        
        db.commit()
        
        # Refresh all created transactions
        for txn in created_transactions:
            db.refresh(txn)
        
        return created_transactions
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )


@router.get("/template/pos")
async def download_pos_template():
    """Download POS transaction template CSV"""
    
    template_data = {
        'transaction_date': ['2024-01-01 10:30:00', '2024-01-01 11:45:00'],
        'amount': [100.50, 250.75],
        'reference_number': ['REF001', 'REF002'],
        'terminal_id': ['TID001', 'TID002'],
        'card_type': ['VISA', 'MASTERCARD'],
        'merchant_name': ['ABC Store', 'XYZ Shop'],
        'batch_number': ['BATCH001', 'BATCH002'],
        'receipt_number': ['RCP001', 'RCP002']
    }
    
    df = pd.DataFrame(template_data)
    
    # Create CSV content
    csv_content = df.to_csv(index=False)
    
    from fastapi.responses import Response
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=pos_transactions_template.csv"}
    )


@router.get("/template/bank")
async def download_bank_template():
    """Download bank transaction template CSV"""
    
    template_data = {
        'transaction_date': ['2024-01-01 10:30:00', '2024-01-01 11:45:00'],
        'amount': [100.50, 250.75],
        'reference_number': ['BANKREF001', 'BANKREF002'],
        'description': ['POS Transaction', 'Card Payment'],
        'card_type': ['VISA', 'MASTERCARD'],
        'terminal_id': ['TID001', 'TID002'],
        'bank_name': ['First Bank', 'Access Bank'],
        'merchant_name': ['ABC Store', 'XYZ Shop']
    }
    
    df = pd.DataFrame(template_data)
    
    # Create CSV content
    csv_content = df.to_csv(index=False)
    
    from fastapi.responses import Response
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=bank_transactions_template.csv"}
    )