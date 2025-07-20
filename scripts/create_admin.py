#!/usr/bin/env python3
"""
Script to create an initial admin user for the POS Reconciliation Dashboard.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine
from backend.models.user import User, UserRole
from backend.services.auth import get_password_hash


def create_admin_user():
    """Create an initial admin user"""
    db = SessionLocal()
    
    try:
        # Check if admin user already exists
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("Admin user already exists!")
            return
        
        # Create admin user
        admin_user = User(
            username="admin",
            email="admin@example.com",
            full_name="System Administrator",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Admin user created successfully!")
        print(f"Username: admin")
        print(f"Password: admin123")
        print(f"Email: admin@example.com")
        
        # Create a sample analyst user
        analyst_user = User(
            username="analyst",
            email="analyst@example.com", 
            full_name="Sample Analyst",
            hashed_password=get_password_hash("analyst123"),
            role=UserRole.ANALYST,
            is_active=True
        )
        
        db.add(analyst_user)
        db.commit()
        
        print("✅ Sample analyst user created!")
        print(f"Username: analyst")
        print(f"Password: analyst123")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Creating initial admin user...")
    create_admin_user()