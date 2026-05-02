import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.job import Job

def clear_sample_jobs():
    db = SessionLocal()
    
    try:
        # Delete all jobs with source='sample'
        sample_jobs = db.query(Job).filter(Job.source == 'sample').all()
        count = len(sample_jobs)
        
        for job in sample_jobs:
            db.delete(job)
        
        db.commit()
        print(f"Deleted {count} sample jobs from database")
        
        # Show remaining jobs
        remaining = db.query(Job).count()
        print(f"Remaining jobs in database: {remaining}")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_sample_jobs()
