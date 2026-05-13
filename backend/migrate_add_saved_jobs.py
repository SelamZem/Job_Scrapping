"""
One-time migration: adds saved_jobs column to users table.
Safe to run multiple times (checks if column exists first).

Usage:
    python migrate_add_saved_jobs.py
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./jobs.db")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
if DATABASE_URL.startswith("postgresql://") and not DATABASE_URL.startswith("postgresql+psycopg"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    if DATABASE_URL.startswith("sqlite"):
        # Check if column exists in SQLite
        result = conn.execute(text("PRAGMA table_info(users)"))
        columns = [row[1] for row in result]
        if "saved_jobs" not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN saved_jobs TEXT DEFAULT '[]'"))
            conn.commit()
            print("✅ Added saved_jobs column to users table (SQLite)")
        else:
            print("ℹ️  saved_jobs column already exists (SQLite)")
    else:
        # PostgreSQL
        result = conn.execute(text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name='users' AND column_name='saved_jobs'
        """))
        if not result.fetchone():
            conn.execute(text("ALTER TABLE users ADD COLUMN saved_jobs TEXT DEFAULT '[]'"))
            conn.commit()
            print("✅ Added saved_jobs column to users table (PostgreSQL)")
        else:
            print("ℹ️  saved_jobs column already exists (PostgreSQL)")
