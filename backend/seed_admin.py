"""
Seed admin user for the application
Run this script to create the default admin user

Usage:
    python seed_admin.py

Default admin credentials:
    Username: admin
    Password: admin123
    Email: admin@carejobs.com
"""

import os
import sys

# Add the app directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.api.auth_new import get_password_hash
from sqlalchemy.orm import Session

def create_admin_user(db: Session):
    """Create default admin user if not exists"""
    
    # Check if admin already exists
    admin = db.query(User).filter(User.username == "admin").first()
    if admin:
        print("✅ Admin user already exists")
        print(f"   Username: {admin.username}")
        print(f"   Email: {admin.email}")
        print(f"   Role: {admin.role}")
        return
    
    # Create admin user
    admin_user = User(
        username="admin",
        email="admin@carejobs.com",
        password_hash=get_password_hash("admin123"),
        role="admin",
        is_active=True
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    print("✅ Admin user created successfully!")
    print(f"   Username: {admin_user.username}")
    print(f"   Password: admin123")
    print(f"   Email: {admin_user.email}")
    print(f"   Role: {admin_user.role}")
    print("\n⚠️  IMPORTANT: Change the default password in production!")

if __name__ == "__main__":
    import os
    
    # Delete old database to recreate with new schema
    db_path = os.path.join(os.path.dirname(__file__), 'jobs.db')
    if os.path.exists(db_path):
        print(f"🗑️  Removing old database: {db_path}")
        os.remove(db_path)
        print("✅ Old database removed")
    
    # Create tables with new schema
    print("🔧 Creating new database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    # Create admin user
    db = SessionLocal()
    try:
        create_admin_user(db)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()
