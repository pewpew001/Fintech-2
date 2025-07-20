from typing import List, Tuple, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz
import numpy as np
from sqlalchemy.orm import Session

from ..models.transaction import BankTransaction, POSTransaction, ReconciliationRecord, TransactionStatus, ReconciliationStatus
from ..models.audit import AuditLog


class ReconciliationEngine:
    """AI-powered reconciliation engine for matching POS and Bank transactions"""
    
    def __init__(self, db: Session):
        self.db = db
        self.match_threshold = 0.85  # Minimum confidence score for auto-matching
        
    def auto_reconcile_batch(self, user_id: int, date_from: datetime, date_to: datetime) -> dict:
        """Perform batch auto-reconciliation for a date range"""
        
        # Get unmatched transactions in the date range
        pos_transactions = self.db.query(POSTransaction).filter(
            POSTransaction.transaction_date >= date_from,
            POSTransaction.transaction_date <= date_to,
            POSTransaction.status == TransactionStatus.PENDING
        ).all()
        
        bank_transactions = self.db.query(BankTransaction).filter(
            BankTransaction.transaction_date >= date_from,
            BankTransaction.transaction_date <= date_to,
            BankTransaction.status == TransactionStatus.PENDING
        ).all()
        
        matches = []
        auto_matched_count = 0
        
        for pos_txn in pos_transactions:
            best_match, confidence = self._find_best_match(pos_txn, bank_transactions)
            
            if best_match and confidence >= self.match_threshold:
                # Create reconciliation record
                reconciliation = ReconciliationRecord(
                    pos_transaction_id=pos_txn.id,
                    bank_transaction_id=best_match.id,
                    reconciliation_status=ReconciliationStatus.AUTO_MATCHED,
                    match_confidence=confidence,
                    amount_difference=abs(pos_txn.amount - best_match.amount),
                    date_difference_hours=self._calculate_date_diff_hours(pos_txn.transaction_date, best_match.transaction_date),
                    reconciled_by=user_id,
                    reconciled_at=datetime.utcnow()
                )
                
                # Update transaction statuses
                pos_txn.status = TransactionStatus.MATCHED
                best_match.status = TransactionStatus.MATCHED
                
                self.db.add(reconciliation)
                matches.append(reconciliation)
                auto_matched_count += 1
                
                # Remove matched bank transaction from the list
                bank_transactions.remove(best_match)
                
                # Log the action
                audit_log = AuditLog(
                    user_id=user_id,
                    action="AUTO_RECONCILE",
                    entity_type="reconciliation_record",
                    entity_id=reconciliation.id,
                    new_values={
                        "pos_transaction_id": pos_txn.id,
                        "bank_transaction_id": best_match.id,
                        "confidence": float(confidence)
                    }
                )
                self.db.add(audit_log)
        
        self.db.commit()
        
        return {
            "auto_matched": auto_matched_count,
            "total_pos_transactions": len(pos_transactions),
            "total_bank_transactions": len(bank_transactions),
            "unmatched_pos": len(pos_transactions) - auto_matched_count,
            "unmatched_bank": len(bank_transactions) - auto_matched_count
        }
    
    def _find_best_match(self, pos_txn: POSTransaction, bank_transactions: List[BankTransaction]) -> Tuple[Optional[BankTransaction], float]:
        """Find the best matching bank transaction for a POS transaction"""
        
        best_match = None
        best_confidence = 0.0
        
        for bank_txn in bank_transactions:
            confidence = self._calculate_match_confidence(pos_txn, bank_txn)
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_match = bank_txn
        
        return best_match, best_confidence
    
    def _calculate_match_confidence(self, pos_txn: POSTransaction, bank_txn: BankTransaction) -> float:
        """Calculate confidence score for matching two transactions"""
        
        # Initialize weights for different matching criteria
        weights = {
            'amount': 0.4,
            'date': 0.2,
            'reference': 0.2,
            'terminal': 0.1,
            'merchant': 0.1
        }
        
        scores = {}
        
        # Amount matching (exact match gets 1.0, close matches get partial scores)
        amount_diff_percentage = abs(float(pos_txn.amount - bank_txn.amount)) / float(pos_txn.amount) if pos_txn.amount > 0 else 1
        if amount_diff_percentage == 0:
            scores['amount'] = 1.0
        elif amount_diff_percentage <= 0.01:  # Within 1%
            scores['amount'] = 0.9
        elif amount_diff_percentage <= 0.05:  # Within 5%
            scores['amount'] = 0.7
        else:
            scores['amount'] = max(0, 1 - amount_diff_percentage)
        
        # Date matching (same day = 1.0, within 1 day = 0.8, etc.)
        date_diff_hours = self._calculate_date_diff_hours(pos_txn.transaction_date, bank_txn.transaction_date)
        if date_diff_hours <= 2:
            scores['date'] = 1.0
        elif date_diff_hours <= 24:
            scores['date'] = 0.8
        elif date_diff_hours <= 48:
            scores['date'] = 0.6
        elif date_diff_hours <= 72:
            scores['date'] = 0.4
        else:
            scores['date'] = max(0, 1 - (date_diff_hours / 168))  # Decay over a week
        
        # Reference number matching (fuzzy matching)
        if pos_txn.reference_number and bank_txn.reference_number:
            scores['reference'] = fuzz.ratio(pos_txn.reference_number, bank_txn.reference_number) / 100.0
        else:
            scores['reference'] = 0.0
        
        # Terminal ID matching
        if pos_txn.terminal_id and bank_txn.terminal_id:
            scores['terminal'] = 1.0 if pos_txn.terminal_id == bank_txn.terminal_id else 0.0
        else:
            scores['terminal'] = 0.0
        
        # Merchant name matching (fuzzy matching)
        if pos_txn.merchant_name and bank_txn.merchant_name:
            scores['merchant'] = fuzz.ratio(pos_txn.merchant_name, bank_txn.merchant_name) / 100.0
        else:
            scores['merchant'] = 0.0
        
        # Calculate weighted confidence score
        confidence = sum(scores[criterion] * weights[criterion] for criterion in weights.keys())
        
        return min(confidence, 1.0)  # Cap at 1.0
    
    def _calculate_date_diff_hours(self, date1: datetime, date2: datetime) -> int:
        """Calculate difference between two dates in hours"""
        return abs(int((date1 - date2).total_seconds() / 3600))
    
    def manual_match(self, user_id: int, pos_transaction_id: int, bank_transaction_id: int, comments: str = None) -> ReconciliationRecord:
        """Manually match a POS transaction with a bank transaction"""
        
        pos_txn = self.db.query(POSTransaction).filter(POSTransaction.id == pos_transaction_id).first()
        bank_txn = self.db.query(BankTransaction).filter(BankTransaction.id == bank_transaction_id).first()
        
        if not pos_txn or not bank_txn:
            raise ValueError("Transaction not found")
        
        # Calculate confidence score for the manual match
        confidence = self._calculate_match_confidence(pos_txn, bank_txn)
        
        # Create reconciliation record
        reconciliation = ReconciliationRecord(
            pos_transaction_id=pos_transaction_id,
            bank_transaction_id=bank_transaction_id,
            reconciliation_status=ReconciliationStatus.MANUALLY_MATCHED,
            match_confidence=confidence,
            amount_difference=abs(pos_txn.amount - bank_txn.amount),
            date_difference_hours=self._calculate_date_diff_hours(pos_txn.transaction_date, bank_txn.transaction_date),
            reconciled_by=user_id,
            reconciled_at=datetime.utcnow(),
            comments=comments
        )
        
        # Update transaction statuses
        pos_txn.status = TransactionStatus.MATCHED
        bank_txn.status = TransactionStatus.MATCHED
        
        self.db.add(reconciliation)
        
        # Log the action
        audit_log = AuditLog(
            user_id=user_id,
            action="MANUAL_RECONCILE",
            entity_type="reconciliation_record",
            entity_id=reconciliation.id,
            new_values={
                "pos_transaction_id": pos_transaction_id,
                "bank_transaction_id": bank_transaction_id,
                "confidence": float(confidence),
                "comments": comments
            }
        )
        self.db.add(audit_log)
        
        self.db.commit()
        return reconciliation
    
    def mark_exception(self, user_id: int, transaction_id: int, transaction_type: str, reason: str, comments: str = None):
        """Mark a transaction as an exception"""
        
        if transaction_type.lower() == "pos":
            txn = self.db.query(POSTransaction).filter(POSTransaction.id == transaction_id).first()
        else:
            txn = self.db.query(BankTransaction).filter(BankTransaction.id == transaction_id).first()
        
        if not txn:
            raise ValueError("Transaction not found")
        
        # Create reconciliation record for exception
        reconciliation = ReconciliationRecord(
            pos_transaction_id=transaction_id if transaction_type.lower() == "pos" else None,
            bank_transaction_id=transaction_id if transaction_type.lower() == "bank" else None,
            reconciliation_status=ReconciliationStatus.EXCEPTION,
            reconciled_by=user_id,
            reconciled_at=datetime.utcnow(),
            comments=comments,
            exception_reason=reason
        )
        
        # Update transaction status
        txn.status = TransactionStatus.EXCEPTION
        
        self.db.add(reconciliation)
        
        # Log the action
        audit_log = AuditLog(
            user_id=user_id,
            action="MARK_EXCEPTION",
            entity_type="reconciliation_record",
            entity_id=reconciliation.id,
            new_values={
                "transaction_id": transaction_id,
                "transaction_type": transaction_type,
                "reason": reason,
                "comments": comments
            }
        )
        self.db.add(audit_log)
        
        self.db.commit()
        return reconciliation