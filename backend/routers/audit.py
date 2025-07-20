from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime

from ..database import get_db
from ..models.user import User, UserRole
from ..models.audit import AuditLog
from ..schemas.audit import AuditLogResponse
from ..services.auth import get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[AuditLogResponse])
def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get audit logs with filtering"""
    
    # Only admin and reviewer roles can view audit logs
    if current_user.role not in [UserRole.ADMIN, UserRole.REVIEWER]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view audit logs")
    
    query = db.query(AuditLog)
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    
    if action:
        query = query.filter(AuditLog.action.ilike(f"%{action}%"))
    
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    
    if date_from:
        query = query.filter(AuditLog.timestamp >= datetime.combine(date_from, datetime.min.time()))
    
    if date_to:
        query = query.filter(AuditLog.timestamp <= datetime.combine(date_to, datetime.max.time()))
    
    logs = query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    return logs


@router.get("/{log_id}", response_model=AuditLogResponse)
def get_audit_log(
    log_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific audit log entry"""
    
    if current_user.role not in [UserRole.ADMIN, UserRole.REVIEWER]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view audit logs")
    
    log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit log not found")
    
    return log


@router.get("/user/{user_id}", response_model=List[AuditLogResponse])
def get_user_audit_logs(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get audit logs for a specific user"""
    
    # Users can view their own audit logs, admin can view all
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    logs = db.query(AuditLog).filter(
        AuditLog.user_id == user_id
    ).order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    
    return logs


@router.get("/actions/summary")
def get_action_summary(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get summary of actions performed in a date range"""
    
    if current_user.role not in [UserRole.ADMIN, UserRole.REVIEWER]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    from sqlalchemy import func
    
    query = db.query(
        AuditLog.action,
        func.count(AuditLog.id).label('count'),
        func.count(func.distinct(AuditLog.user_id)).label('unique_users')
    ).group_by(AuditLog.action)
    
    if date_from:
        query = query.filter(AuditLog.timestamp >= datetime.combine(date_from, datetime.min.time()))
    
    if date_to:
        query = query.filter(AuditLog.timestamp <= datetime.combine(date_to, datetime.max.time()))
    
    results = query.all()
    
    summary = []
    for action, count, unique_users in results:
        summary.append({
            "action": action,
            "count": count,
            "unique_users": unique_users
        })
    
    return {"summary": summary}


@router.get("/users/activity")
def get_user_activity(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user activity summary"""
    
    if current_user.role not in [UserRole.ADMIN, UserRole.REVIEWER]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    from sqlalchemy import func
    
    query = db.query(
        AuditLog.user_id,
        User.username,
        User.full_name,
        func.count(AuditLog.id).label('total_actions'),
        func.max(AuditLog.timestamp).label('last_activity')
    ).join(User, AuditLog.user_id == User.id).group_by(
        AuditLog.user_id, User.username, User.full_name
    )
    
    if date_from:
        query = query.filter(AuditLog.timestamp >= datetime.combine(date_from, datetime.min.time()))
    
    if date_to:
        query = query.filter(AuditLog.timestamp <= datetime.combine(date_to, datetime.max.time()))
    
    results = query.all()
    
    activity = []
    for user_id, username, full_name, total_actions, last_activity in results:
        activity.append({
            "user_id": user_id,
            "username": username,
            "full_name": full_name,
            "total_actions": total_actions,
            "last_activity": last_activity
        })
    
    return {"user_activity": activity}