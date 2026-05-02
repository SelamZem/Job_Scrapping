import sys
import os

# Add the parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.job import Job

def clear_all_jobs():
    db = SessionLocal()
    try:
        count = db.query(Job).count()
        db.query(Job).delete()
        db.commit()
        print(f"Cleared {count} jobs from database")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_all_jobs()
